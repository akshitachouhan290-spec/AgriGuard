"""
Plant.id service.

This module contains the actual Plant.id API integration.
The API key is loaded from the PLANT_ID_API_KEY environment variable.
"""

import os
import base64

import httpx
from fastapi import HTTPException


PLANT_ID_URL = "https://api.plant.id/v3/identification"


async def analyze_with_plant_id(
    image_bytes: bytes,
    filename: str | None = None,
):
    """
    Send an image to Plant.id for plant health/disease analysis
    and return a clean response for the application.
    """

    # ---------- 1. API key check ----------
    api_key = os.getenv("PLANT_ID_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "Server misconfiguration: "
                "PLANT_ID_API_KEY environment variable not set."
            ),
        )

    # ---------- 2. Basic image validation ----------
    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    # ---------- 3. Prepare request for Plant.id ----------
    # Plant.id v3 expects images as base64 encoded strings.
    encoded_image = base64.b64encode(image_bytes).decode("ascii")

    headers = {
        "Content-Type": "application/json",
        "Api-Key": api_key,
    }

    payload = {
        "images": [encoded_image],
        "health": "only",
    }

    # ---------- 4. Call Plant.id ----------
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                PLANT_ID_URL,
                headers=headers,
                json=payload,
            )

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

    # ---------- 5. Handle Plant.id errors ----------
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
            detail=(
                "Plant.id API is currently unavailable. "
                "Please try again later."
            ),
        )

    if response.status_code not in (200, 201):
        raise HTTPException(
            status_code=502,
            detail=(
                f"Unexpected response from Plant.id "
                f"(status {response.status_code})."
            ),
        )

    data = response.json()

    # ---------- 6. Extract Plant.id result ----------
    result = data.get("result", {})

    is_healthy_info = result.get("is_healthy", {})

    disease_suggestions = (
        result.get("disease", {}).get("suggestions", [])
    )

    top_disease_name = (
        disease_suggestions[0]["name"]
        if disease_suggestions
        else None
    )

    top_disease_probability = (
        disease_suggestions[0]["probability"]
        if disease_suggestions
        else None
    )

    clean_disease_suggestions = [
        {
            "name": disease.get("name"),
            "probability": disease.get("probability"),
        }
        for disease in disease_suggestions
    ]

    # ---------- 7. Return clean Plant.id result ----------
    return {
        "filename": filename,
        "status": data.get("status"),
        "is_healthy": is_healthy_info.get("binary"),
        "is_healthy_probability": is_healthy_info.get("probability"),
        "top_disease": top_disease_name,
        "top_disease_probability": top_disease_probability,
        "disease_suggestions": clean_disease_suggestions,
    }