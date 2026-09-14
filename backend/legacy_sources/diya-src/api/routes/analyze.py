import os
import sys
import base64

import httpx
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database import crud, models
from src.logger import get_logger
from src.exception import CustomException
from dotenv import load_dotenv
load_dotenv()

logger = get_logger(__name__)

router = APIRouter(prefix="/analyze", tags=["Analysis"])

PLANT_ID_URL = "https://api.plant.id/v3/identification"

# Confidence below this threshold gets auto-flagged for expert review,
# same pattern already used for the Kindwise-style manual entry flow.
CONFIDENCE_REVIEW_THRESHOLD_PERCENT = 70.0


@router.post("/")
async def analyze_disease(
    farmer_id: int = Form(...),
    field_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    

    # ---------- 1. Validate farmer + field belong together ----------
    # Same validation pattern as disease_routes.py -- gives a clear error
    # instead of a raw DB integrity failure from the composite foreign key.
    farmer = crud.get_farmer_by_id(db, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    field = crud.get_field_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    if field.farmer_id != farmer_id:
        raise HTTPException(
            status_code=400,
            detail="Field does not belong to the specified farmer",
        )

    # ---------- 2. API key check ----------
    api_key = os.getenv("PLANT_ID_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: PLANT_ID_API_KEY environment variable not set.",
        )

    # ---------- 3. Basic image validation ----------
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Please upload an image.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    # ---------- 4. Call Plant.id ----------
    encoded_image = base64.b64encode(image_bytes).decode("ascii")
    headers = {"Content-Type": "application/json", "Api-Key": api_key}
    payload = {"images": [encoded_image], "health": "only"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(PLANT_ID_URL, headers=headers, json=payload)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Plant.id API request timed out. Please try again.")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Plant.id API: {exc}")

    if response.status_code == 400:
        raise HTTPException(status_code=400, detail="Plant.id rejected the request (bad image or bad format).")
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Plant.id authentication failed. Check PLANT_ID_API_KEY.")
    if response.status_code == 429:
        raise HTTPException(status_code=429, detail="Plant.id: not enough credits.")
    if response.status_code >= 500:
        raise HTTPException(status_code=502, detail="Plant.id API is currently unavailable. Please try again later.")
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Unexpected response from Plant.id (status {response.status_code}).")

    data = response.json()

    # ---------- 5. Extract fields confirmed by official docs ----------
    result = data.get("result", {})
    is_healthy_info = result.get("is_healthy", {})
    disease_suggestions = result.get("disease", {}).get("suggestions", [])

    is_healthy = is_healthy_info.get("binary")
    top_disease_name = disease_suggestions[0]["name"] if disease_suggestions else None
    top_disease_probability = disease_suggestions[0]["probability"] if disease_suggestions else None

    clean_disease_suggestions = [
        {"name": d.get("name"), "probability": d.get("probability")}
        for d in disease_suggestions
    ]

    # Store confidence on ONE consistent scale (0-100). Plant.id gives 0-1.
    confidence = round(top_disease_probability * 100, 2) if top_disease_probability is not None else None

    # If nothing detected and plant is healthy, say so plainly instead of leaving null.
    disease_label = top_disease_name if top_disease_name else ("Healthy" if is_healthy else "Unknown")

    # Low-confidence results get flagged for expert review rather than
    # silently trusted -- this is the "expert validation" workflow piece.
    status = (
        models.AnalysisStatus.needs_review
        if (confidence is not None and confidence < CONFIDENCE_REVIEW_THRESHOLD_PERCENT)
        else models.AnalysisStatus.auto_confirmed
    )

    # ---------- 6. Save to database ----------
    # crop comes from the field's registered crop (via crop_id -> Crop.name),
    # NOT from Plant.id -- health="only" mode does not identify species.
    # severity is intentionally None -- not fabricated from probability.
    try:
        analysis = crud.create_disease_analysis(
            db,
            farmer_id=farmer_id,
            field_id=field_id,
            image_ref=file.filename,
            crop=field.crop.name if field.crop else None,
            disease=disease_label,
            confidence=confidence,
            severity=None,
            status=status,
        )
    except CustomException:
        raise
    except Exception as e:
        logger.error("Failed to save disease analysis after Plant.id call")
        raise CustomException(e, sys)

    # ---------- 7. Response ----------
    return {
        "analysis_id": analysis.id,
        "farmer_id": farmer_id,
        "field_id": field_id,
        "filename": file.filename,
        "status": analysis.status,
        "is_healthy": is_healthy,
        "is_healthy_probability": is_healthy_info.get("probability"),
        "top_disease": top_disease_name,
        "top_disease_probability": top_disease_probability,
        "confidence": confidence,
        "disease_suggestions": clean_disease_suggestions,
    }