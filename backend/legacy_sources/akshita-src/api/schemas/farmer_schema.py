from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FarmerCreate(BaseModel):
    name: str
    phone: str
    language: Optional[str] = "English"
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class FarmerResponse(BaseModel):
    id: int
    name: str
    phone: str
    language: str
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True