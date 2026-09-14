from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database import crud
from src.api.schemas.crop_schema import CropResponse


router = APIRouter(
    prefix="/crops",
    tags=["Crops"]
)


# ---------------- Get All Crops ----------------

@router.get("/", response_model=List[CropResponse])
def list_crops(
    db: Session = Depends(get_db)
):
    return crud.get_all_crops(db)


# ---------------- Get Crop by Name ----------------

@router.get("/name/{name}", response_model=CropResponse)
def get_crop_by_name(
    name: str,
    db: Session = Depends(get_db)
):
    crop = crud.get_crop_by_name(
        db,
        name
    )

    if not crop:
        raise HTTPException(
            status_code=404,
            detail="Crop not found"
        )

    return crop


# ---------------- Get Crop by ID ----------------

@router.get("/{crop_id}", response_model=CropResponse)
def get_crop(
    crop_id: int,
    db: Session = Depends(get_db)
):
    crop = crud.get_crop_by_id(
        db,
        crop_id
    )

    if not crop:
        raise HTTPException(
            status_code=404,
            detail="Crop not found"
        )

    return crop
