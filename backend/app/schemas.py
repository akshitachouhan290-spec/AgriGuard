from typing import Optional
from pydantic import BaseModel, Field

class FarmerRegister(BaseModel):
    name: str
    phone: str
    language: str = "Hindi"
    village: str = ""
    district: str = ""
    state: str = ""
    latitude: float = 26.9124
    longitude: float = 75.7873
    main_crop: str = "Tomato"
    field_size: float = 2.0
    password: str = "demo123"

class FarmerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    language: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FieldCreate(BaseModel):
    farmer_id: int
    field_name: str = Field(min_length=1)
    crop_id: int
    area: float = 0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: str = ""

class ChatRequest(BaseModel):
    message: str
