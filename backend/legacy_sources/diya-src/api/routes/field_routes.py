from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database import crud
from src.api.schemas.field_schema import FieldCreate, FieldResponse


router = APIRouter(
    prefix="/fields",
    tags=["Fields"]
)


# ---------------- Field Update Schema ----------------

class FieldUpdate(BaseModel):
    field_name: Optional[str] = None
    crop_id: Optional[int] = None
    area: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# ---------------- Create Field ----------------

@router.post("/", response_model=FieldResponse)
def add_field(
    field: FieldCreate,
    db: Session = Depends(get_db)
):
    farmer = crud.get_farmer_by_id(
        db,
        field.farmer_id
    )

    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    crop = crud.get_crop_by_id(
        db,
        field.crop_id
    )

    if not crop:
        raise HTTPException(
            status_code=404,
            detail="Crop not found in catalog"
        )

    return crud.create_field(
        db,
        **field.model_dump()
    )


# ---------------- Get Field ----------------

@router.get("/{field_id}", response_model=FieldResponse)
def get_field(
    field_id: int,
    db: Session = Depends(get_db)
):
    field = crud.get_field_by_id(
        db,
        field_id
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    return field


# ---------------- Get Fields by Farmer ----------------

@router.get(
    "/farmer/{farmer_id}",
    response_model=List[FieldResponse]
)
def list_fields_for_farmer(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    farmer = crud.get_farmer_by_id(
        db,
        farmer_id
    )

    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    return crud.get_fields_by_farmer(
        db,
        farmer_id
    )


# ---------------- Update Field ----------------

@router.patch(
    "/{field_id}",
    response_model=FieldResponse
)
def update_field(
    field_id: int,
    field_data: FieldUpdate,
    db: Session = Depends(get_db)
):
    field = crud.get_field_by_id(
        db,
        field_id
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    # If crop is being changed, make sure the new crop
    # exists in the master crop catalog.
    if field_data.crop_id is not None:
        crop = crud.get_crop_by_id(
            db,
            field_data.crop_id
        )

        if not crop:
            raise HTTPException(
                status_code=404,
                detail="Crop not found in catalog"
            )

    update_data = field_data.model_dump(
        exclude_unset=True
    )

    return crud.update_field(
        db,
        field_id,
        **update_data
    )


# ---------------- Delete Field ----------------

@router.delete("/{field_id}")
def delete_field(
    field_id: int,
    db: Session = Depends(get_db)
):
    field = crud.get_field_by_id(
        db,
        field_id
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    crud.delete_field(
        db,
        field_id
    )

    return {
        "message": "Field deleted successfully",
        "field_id": field_id
    }
