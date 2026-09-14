from typing import Optional

from pydantic import BaseModel


class CropCreate(BaseModel):
    name: str
    category: Optional[str] = None
    typical_growth_duration_days: Optional[int] = None
    common_diseases_note: Optional[str] = None


class CropResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    typical_growth_duration_days: Optional[int] = None
    common_diseases_note: Optional[str] = None

    class Config:
        from_attributes = True

   