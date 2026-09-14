import datetime
from typing import Optional
from pydantic import BaseModel, Field, AliasChoices, field_validator, ConfigDict
import re

class FarmerRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the farmer")
    phone: str = Field(
        ..., 
        validation_alias=AliasChoices("phone", "mobile", "mobile_number", "mobile number"),
        description="Mobile or phone number"
    )
    language: str = Field(
        ..., 
        validation_alias=AliasChoices("language", "preferred_language", "preferred language"),
        description="Preferred language of the farmer"
    )
    village: str = Field(..., min_length=1, description="Village name")
    district: str = Field(..., min_length=1, description="District name")
    state: str = Field(..., min_length=1, description="State name")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude GPS coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude GPS coordinate")
    main_crop: str = Field(
        ..., 
        validation_alias=AliasChoices("main_crop", "main crop"),
        description="Main crop grown by the farmer"
    )
    field_size: float = Field(
        ..., 
        ge=0.0, 
        validation_alias=AliasChoices("field_size", "approximate_field_size", "approximate field size"),
        description="Approximate field size in acres/hectares"
    )
    password: str = Field(..., min_length=6, description="Security password (min 6 characters)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Test Farmer",
                "phone": "9876543210",
                "language": "English",
                "village": "Test Village",
                "district": "Jaipur",
                "state": "Rajasthan",
                "latitude": 26.9124,
                "longitude": 75.7873,
                "main_crop": "Tomato",
                "field_size": 2.5,
                "password": "Test@12345"
            }
        }
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Strip spaces and dashes
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        # Validate format: basic international format check, 7 to 15 digits
        if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
            raise ValueError("Invalid phone number format. Must contain 7 to 15 digits, optionally starting with '+'")
        return cleaned

class FarmerLogin(BaseModel):
    phone: str = Field(
        ..., 
        validation_alias=AliasChoices("phone", "mobile", "mobile_number", "mobile number"),
        description="Mobile phone number used during registration"
    )
    password: str = Field(..., description="Farmer's login password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "phone": "9876543210",
                "password": "Test@12345"
            }
        }
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned

class FarmerResponse(BaseModel):
    id: int
    name: str
    phone: str
    language: str
    village: str
    district: str
    state: str
    latitude: float
    longitude: float
    main_crop: str
    field_size: float
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    farmer_id: Optional[int] = None
