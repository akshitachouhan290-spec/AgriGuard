import enum

from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    ForeignKey, ForeignKeyConstraint, UniqueConstraint,
    DateTime, Text, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.db import Base


class AnalysisStatus(str, enum.Enum):
    auto_confirmed = "auto_confirmed"
    needs_review = "needs_review"
    reviewed = "reviewed"


class RiskLevel(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    language = Column(String(20), default="English")
    village = Column(String(100))
    district = Column(String(100))
    state = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    is_officer = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ondelete + passive_deletes: deleting a farmer cascades down through
    # fields -> disease_analyses/soil_analyses/weather/sensor_readings -> risk,
    # enforced by the database itself, not just by SQLAlchemy in Python.
    fields = relationship(
        "Field", back_populates="farmer",
        cascade="all, delete-orphan", passive_deletes=True,
    )
    disease_analyses = relationship(
        "DiseaseAnalysis", back_populates="farmer",
        foreign_keys="[DiseaseAnalysis.farmer_id]",
        overlaps="field,disease_analyses",
    )
    soil_analyses = relationship(
        "SoilAnalysis", back_populates="farmer",
        foreign_keys="[SoilAnalysis.farmer_id]",
        overlaps="field,soil_analyses",
    )


class Crop(Base):
    """
    Master/reference table — a fixed catalog of crops (Wheat, Rice, Tomato...).
    NOT linked to a specific farmer or field directly. Fields point INTO this
    table via crop_id, which keeps crop names consistent (no "Tomato" vs
    "tomato" vs "Tomatoes" issue) and gives us a place to store crop-level
    metadata (growth duration etc.) for future risk-engine use.
    """
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True)
    typical_growth_duration_days = Column(Integer, nullable=True)
    common_diseases_note = Column(Text, nullable=True)

    fields = relationship("Field", back_populates="crop")


class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    area = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    soil_type = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # This composite unique constraint is what makes the composite foreign
    # keys on DiseaseAnalysis/SoilAnalysis possible — it lets the DB verify
    # a (field_id, farmer_id) PAIR, not just each id individually.
    __table_args__ = (
        UniqueConstraint("id", "farmer_id", name="uq_field_id_farmer_id"),
    )

    farmer = relationship("Farmer", back_populates="fields")
    crop = relationship("Crop", back_populates="fields")

    disease_analyses = relationship(
        "DiseaseAnalysis", back_populates="field",
        foreign_keys="[DiseaseAnalysis.field_id, DiseaseAnalysis.farmer_id]",
        cascade="all, delete-orphan", passive_deletes=True,
        overlaps="disease_analyses,farmer",
    )
    soil_analyses = relationship(
        "SoilAnalysis", back_populates="field",
        foreign_keys="[SoilAnalysis.field_id, SoilAnalysis.farmer_id]",
        cascade="all, delete-orphan", passive_deletes=True,
        overlaps="soil_analyses,farmer",
    )
    weather_records = relationship(
        "Weather", back_populates="field",
        cascade="all, delete-orphan", passive_deletes=True,
    )
    sensor_readings = relationship(
        "SensorReading", back_populates="field",
        cascade="all, delete-orphan", passive_deletes=True,
    )


class DiseaseAnalysis(Base):
    __tablename__ = "disease_analyses"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(Integer, nullable=False)  # validity enforced via composite FK below
    image_ref = Column(String(255))
    crop = Column(String(50))  # raw crop name as detected by the AI on the photo itself —
                                 # intentionally NOT linked to the Crop master table, since
                                 # a mismatch here (field says Tomato, AI sees Wheat) is a
                                 # useful signal, not something we want to silently normalize.
    disease = Column(String(100))
    confidence = Column(Float)
    severity = Column(String(20))
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.auto_confirmed)
    confirmed_disease = Column(String(100), nullable=True)
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # THE FIX: instead of two independent foreign keys (field_id -> fields.id,
    # farmer_id -> farmers.id) that can be individually valid but mismatched,
    # this composite constraint forces the (field_id, farmer_id) pair to match
    # an actual row in fields(id, farmer_id). A mismatched combination is now
    # rejected by PostgreSQL itself, not just by our API-layer check.
    __table_args__ = (
        ForeignKeyConstraint(
            ["field_id", "farmer_id"],
            ["fields.id", "fields.farmer_id"],
            ondelete="CASCADE",
            name="fk_disease_field_farmer",
        ),
    )

    farmer = relationship(
        "Farmer", back_populates="disease_analyses",
        foreign_keys=[farmer_id], overlaps="field,disease_analyses",
    )
    field = relationship(
        "Field", back_populates="disease_analyses",
        foreign_keys=[field_id, farmer_id], overlaps="farmer,disease_analyses",
    )
    risk = relationship(
        "Risk", back_populates="analysis",
        uselist=False, cascade="all, delete-orphan", passive_deletes=True,
    )


class SoilAnalysis(Base):
    """
    Same farmer/field mismatch risk existed here as in DiseaseAnalysis —
    fixed the same way, with a composite foreign key.
    """
    __tablename__ = "soil_analyses"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(Integer, nullable=False)
    image_ref = Column(String(255))
    soil_type = Column(String(50))
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(
            ["field_id", "farmer_id"],
            ["fields.id", "fields.farmer_id"],
            ondelete="CASCADE",
            name="fk_soil_field_farmer",
        ),
    )

    farmer = relationship(
        "Farmer", back_populates="soil_analyses",
        foreign_keys=[farmer_id], overlaps="field,soil_analyses",
    )
    field = relationship(
        "Field", back_populates="soil_analyses",
        foreign_keys=[field_id, farmer_id], overlaps="farmer,soil_analyses",
    )


class Weather(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    rain = Column(Boolean, default=False)
    wind = Column(Float)
    date = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", back_populates="weather_records")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("disease_analyses.id", ondelete="CASCADE"), nullable=False, unique=True)
    risk_level = Column(Enum(RiskLevel))
    risk_score = Column(Float)
    reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analysis = relationship("DiseaseAnalysis", back_populates="risk")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    sensor_type = Column(String(50))
    value = Column(Float)
    unit = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    field = relationship("Field", back_populates="sensor_readings")