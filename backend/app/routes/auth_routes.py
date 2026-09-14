from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Farmer
from ..schemas import FarmerRegister
from ..security import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register(payload: FarmerRegister, db: Session = Depends(get_db)):
    if db.query(Farmer).filter(Farmer.phone == payload.phone).first():
        raise HTTPException(400, "Phone number already registered")
    farmer = Farmer(name=payload.name, phone=payload.phone, language=payload.language,
                    village=payload.village, district=payload.district, state=payload.state,
                    latitude=payload.latitude, longitude=payload.longitude,
                    password_hash=hash_password(payload.password))
    db.add(farmer); db.commit(); db.refresh(farmer)
    return farmer_response(farmer)

@router.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    farmer = db.query(Farmer).filter(Farmer.phone == payload.get("phone")).first()
    if not farmer or not verify_password(payload.get("password",""), farmer.password_hash):
        raise HTTPException(401, "Invalid mobile number or password")
    return {"access_token": create_token(farmer.id), "token_type": "bearer", "farmer_id": farmer.id}

def farmer_response(f):
    return {"id":f.id,"name":f.name,"phone":f.phone,"language":f.language,"village":f.village or "",
            "district":f.district or "","state":f.state or "","latitude":f.latitude,"longitude":f.longitude,
            "created_at":f.created_at}
