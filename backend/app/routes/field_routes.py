from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Field, Crop
from ..schemas import FieldCreate
router=APIRouter(prefix="/fields",tags=["Fields"])

def out(f):
    return {"id":f.id,"farmer_id":f.farmer_id,"field_name":f.field_name,"crop_id":f.crop_id,
            "crop":f.crop.name if f.crop else "Unknown","area":f.area or 0,"latitude":f.latitude,
            "longitude":f.longitude,"soil_type":f.soil_type,"location":f.location_label or "",
            "lastAnalysis":f.last_analysis,"currentRisk":f.current_risk,"diseaseDetected":f.disease_detected,
            "severity":f.severity}

@router.get("/farmer/{farmer_id}")
def list_fields(farmer_id:int,db:Session=Depends(get_db)):
    return [out(f) for f in db.query(Field).options(joinedload(Field.crop)).filter(Field.farmer_id==farmer_id).order_by(Field.id).all()]

@router.post("/")
def create_field(payload:FieldCreate,db:Session=Depends(get_db)):
    if not db.get(Crop,payload.crop_id): raise HTTPException(404,"Crop not found")
    f=Field(farmer_id=payload.farmer_id,field_name=payload.field_name,crop_id=payload.crop_id,
            area=payload.area,latitude=payload.latitude,longitude=payload.longitude,location_label=payload.location)
    db.add(f); db.commit(); db.refresh(f)
    f=db.query(Field).options(joinedload(Field.crop)).get(f.id)
    return out(f)
