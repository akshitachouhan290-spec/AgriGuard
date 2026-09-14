from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FieldCreate(BaseModel):
    farmer_id: int
    field_name: str
    crop_id: int
    area: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FieldResponse(BaseModel):
    id: int
    farmer_id: int
    field_name: str
    crop_id: int
    area: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    soil_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True