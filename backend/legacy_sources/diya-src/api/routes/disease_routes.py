from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database import crud
from src.database import models
from src.api.schemas.disease_schema import (
    DiseaseAnalysisCreate,
    DiseaseAnalysisResponse,
    DiseaseAnalysisUpdate,
)


router = APIRouter(
    prefix="/disease-analysis",
    tags=["Disease Analysis"]
)


# ---------------- Create Disease Analysis ----------------

@router.post("/", response_model=DiseaseAnalysisResponse)
def create_analysis(
    analysis: DiseaseAnalysisCreate,
    db: Session = Depends(get_db)
):
    """
    NOTE: For now this endpoint just stores a result you pass in.
    Once Kindwise is integrated, this will instead accept an uploaded image,
    call Kindwise internally, and save the returned result automatically.

    The app-level farmer/field validation stays even after the DB-level
    composite foreign key was added. This gives a clear, friendly error
    instead of a raw database integrity error.

    The DB-level composite foreign key remains the final safety net for
    any path that does not go through this API route.
    """

    farmer = crud.get_farmer_by_id(
        db,
        analysis.farmer_id
    )

    if not farmer:
        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    field = crud.get_field_by_id(
        db,
        analysis.field_id
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found"
        )

    if field.farmer_id != analysis.farmer_id:
        raise HTTPException(
            status_code=400,
            detail="Field does not belong to the specified farmer"
        )

    return crud.create_disease_analysis(
        db,
        **analysis.model_dump()
    )


# ---------------- Get Disease History ----------------

@router.get(
    "/field/{field_id}",
    response_model=List[DiseaseAnalysisResponse]
)
def get_field_history(
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

    return crud.get_analyses_by_field(
        db,
        field_id
    )


# ---------------- Update Disease Analysis ----------------

@router.patch(
    "/{analysis_id}",
    response_model=DiseaseAnalysisResponse
)
def update_analysis(
    analysis_id: int,
    analysis_data: DiseaseAnalysisUpdate,
    db: Session = Depends(get_db)
):
    analysis = crud.get_analyses_by_field

    existing = (
        db.query(models.DiseaseAnalysis)
        .filter(models.DiseaseAnalysis.id == analysis_id)
        .first()
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Disease analysis not found"
        )

    update_data = analysis_data.model_dump(
        exclude_unset=True
    )

    return crud.update_disease_analysis(
        db,
        analysis_id,
        **update_data
    )


# ---------------- Delete Disease Analysis ----------------

@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(models.DiseaseAnalysis)
        .filter(models.DiseaseAnalysis.id == analysis_id)
        .first()
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Disease analysis not found"
        )

    crud.delete_disease_analysis(
        db,
        analysis_id
    )

    return {
        "message": "Disease analysis deleted successfully",
        "analysis_id": analysis_id
    }
