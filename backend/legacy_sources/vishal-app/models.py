import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    language = Column(String, nullable=False)
    village = Column(String, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    main_crop = Column(String, nullable=False)
    field_size = Column(Float, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
