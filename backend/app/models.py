from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    language = Column(String(30), default="Hindi")
    village = Column(String(100), default="")
    district = Column(String(100), default="")
    state = Column(String(100), default="")
    latitude = Column(Float, default=26.9124)
    longitude = Column(Float, default=75.7873)
    password_hash = Column(String(255), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fields = relationship("Field", back_populates="farmer", cascade="all, delete-orphan")
    analyses = relationship("DiseaseAnalysis", back_populates="farmer", cascade="all, delete-orphan")

class Crop(Base):
    __tablename__ = "crops"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    category = Column(String(80))
    fields = relationship("Field", back_populates="crop")

class Field(Base):
    __tablename__ = "fields"
    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    area = Column(Float, default=0)
    latitude = Column(Float)
    longitude = Column(Float)
    soil_type = Column(String(50))
    last_analysis = Column(String(50), default="Never")
    current_risk = Column(String(20), default="Low")
    disease_detected = Column(String(100), default="Healthy")
    severity = Column(String(30), default="None")
    location_label = Column(String(200), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    farmer = relationship("Farmer", back_populates="fields")
    crop = relationship("Crop", back_populates="fields")

class DiseaseAnalysis(Base):
    __tablename__ = "disease_analyses"
    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    image_ref = Column(String(255), default="")
    crop = Column(String(80), nullable=False)
    disease = Column(String(120), nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(30), default="Moderate")
    risk = Column(String(20), default="Medium")
    why_json = Column(Text, default="[]")
    advice_json = Column(Text, default="[]")
    status = Column(String(30), default="auto_confirmed")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    farmer = relationship("Farmer", back_populates="analyses")
