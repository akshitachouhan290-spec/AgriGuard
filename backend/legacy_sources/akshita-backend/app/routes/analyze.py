"""
Disease/Plant Health Analysis API (real Plant.id v3 integration)

Farmer image upload karta hai -> hum Plant.id API ko 'health: only'
JSON body attribute ke saath bhejte hain -> Plant.id se real disease/health
result aata hai -> hum use clean JSON mein convert karke return karte hain.

API key kabhi bhi source code mein nahi likhi jaati.
Ye environment variable PLANT_ID_API_KEY se load hoti hai.
"""

import os
import base64

import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

PLANT_ID_URL = "https://api.plant.id/v3/identification"


@router.post("/api/analyze")
async def analyze_disease(file: UploadFile = File(...)):
    """
    Farmer se image leta hai, Plant.id API ko health assessment ke liye
    bhejta hai, aur clean disease/health result return karta hai.
    """

    # ---------- 1. API key check ----------
    api_key = os.getenv("PLANT_ID_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Server misconfiguration: PLANT_ID_API_KEY environment variable not set.",
        )

    # ---------- 2. Basic image validation ----------
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Please upload an image.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    # ---------- 3. Prepare request for Plant.id ----------
    # Plant.id v3 expects images as a list of base64-encoded strings, sent as JSON.
    encoded_image = base64.b64encode(image_bytes).decode("ascii")

    headers = {
        "Content-Type": "application/json",
        "Api-Key": api_key,
    }

    # Per official Plant.id v3 documentation:
    # "health" is a JSON body attribute (NOT a query parameter).
    # health="only" -> response contains only health assessment
    # (result.is_healthy + result.disease.suggestions)
    payload = {
        "images": [encoded_image],
        "health": "only",
    }

    # ---------- 4. Call Plant.id ----------
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(PLANT_ID_URL, headers=headers, json=payload)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Plant.id API request timed out. Please try again.",
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach Plant.id API: {exc}",
        )

    # ---------- 5. Handle Plant.id error responses (per official response codes table) ----------
    if response.status_code == 400:
        raise HTTPException(
            status_code=400,
            detail="Plant.id rejected the request (bad image or bad format).",
        )
    if response.status_code == 401:
        raise HTTPException(
            status_code=401,
            detail="Plant.id authentication failed. Check PLANT_ID_API_KEY.",
        )
    if response.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail="Plant.id: not enough credits.",
        )
    if response.status_code >= 500:
        raise HTTPException(
            status_code=502,
            detail="Plant.id API is currently unavailable. Please try again later.",
        )
    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=502,
            detail=f"Unexpected response from Plant.id (status {response.status_code}).",
        )

    data = response.json()

    # ---------- 6. Extract only the fields confirmed by official docs ----------
    result = data.get("result", {})
    is_healthy_info = result.get("is_healthy", {})
    disease_suggestions = result.get("disease", {}).get("suggestions", [])

    top_disease_name = disease_suggestions[0]["name"] if disease_suggestions else None
    top_disease_probability = (
        disease_suggestions[0]["probability"] if disease_suggestions else None
    )

    clean_disease_suggestions = [
        {"name": d.get("name"), "probability": d.get("probability")}
        for d in disease_suggestions
    ]

    # ---------- 7. Clean response for our frontend ----------
    return {
        "filename": file.filename,
        "status": data.get("status"),
        "is_healthy": is_healthy_info.get("binary"),
        "is_healthy_probability": is_healthy_info.get("probability"),
        "top_disease": top_disease_name,
        "top_disease_probability": top_disease_probability,
        "disease_suggestions": clean_disease_suggestions,
    }