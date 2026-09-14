
import sys
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.db import get_db
from src.database import crud
from src.api.schemas.farmer_schema import FarmerCreate, FarmerResponse
from src.logger import get_logger
from src.exception import CustomException


logger = get_logger(__name__)

router = APIRouter(
    prefix="/farmers",
    tags=["Farmers"]
)


# ---------------- Farmer Update Schema ----------------

class FarmerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# ---------------- Create Farmer ----------------

@router.post("/", response_model=FarmerResponse)
def register_farmer(
    farmer: FarmerCreate,
    db: Session = Depends(get_db)
):
    try:
        existing = crud.get_farmer_by_phone(db, farmer.phone)

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Farmer with this phone already exists"
            )

        return crud.create_farmer(
            db,
            **farmer.model_dump()
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error("Failed to register farmer")
        raise CustomException(e, sys)


# ---------------- Get Farmer ----------------

@router.get("/{farmer_id}", response_model=FarmerResponse)
def get_farmer(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    farmer = crud.get_farmer_by_id(db, farmer_id)

    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    return farmer


# ---------------- Update Farmer ----------------

@router.patch("/{farmer_id}", response_model=FarmerResponse)
def update_farmer(
    farmer_id: int,
    farmer_data: FarmerUpdate,
    db: Session = Depends(get_db)
):
    try:
        # Check whether farmer exists
        farmer = crud.get_farmer_by_id(db, farmer_id)

        if not farmer:
            raise HTTPException(
                status_code=404,
                detail="Farmer not found"
            )

        # If phone is being changed, make sure another farmer
        # is not already using that phone number.
        if farmer_data.phone is not None:
            existing = crud.get_farmer_by_phone(
                db,
                farmer_data.phone
            )

            if existing and existing.id != farmer_id:
                raise HTTPException(
                    status_code=400,
                    detail="Farmer with this phone already exists"
                )

        # Only send fields that were actually provided.
        update_data = farmer_data.model_dump(
            exclude_unset=True
        )

        return crud.update_farmer(
            db,
            farmer_id,
            **update_data
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Failed to update farmer: id={farmer_id}"
        )
        raise CustomException(e, sys)


# ---------------- Delete Farmer ----------------

@router.delete("/{farmer_id}")
def delete_farmer(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    try:
        # Check whether farmer exists
        farmer = crud.get_farmer_by_id(db, farmer_id)

        if not farmer:
            raise HTTPException(
                status_code=404,
                detail="Farmer not found"
            )

        crud.delete_farmer(
            db,
            farmer_id
        )

        return {
            "message": "Farmer deleted successfully",
            "farmer_id": farmer_id
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            f"Failed to delete farmer: id={farmer_id}"
        )
        raise CustomException(e, sys)
