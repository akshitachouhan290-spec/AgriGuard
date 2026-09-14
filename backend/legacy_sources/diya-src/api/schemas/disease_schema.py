from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from src.database.models import AnalysisStatus

class DiseaseAnalysisCreate(BaseModel):
    farmer_id: int
    field_id: int
    image_ref: str
    crop: str
    disease: str
    confidence: float
    severity: str
    


class DiseaseAnalysisUpdate(BaseModel):
    disease: Optional[str] = None
    confidence: Optional[float] = None
    severity: Optional[str] = None
    status: Optional[AnalysisStatus] = None
    confirmed_disease: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class DiseaseAnalysisResponse(BaseModel):
    id: int
    farmer_id: int
    field_id: int
    image_ref: str
    crop: str
    disease: str
    confidence: float
    severity: Optional[str] = None
    status: AnalysisStatus
    created_at: datetime

    class Config:
        from_attributes = True
