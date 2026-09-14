from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Farmer
from ..schemas import FarmerUpdate
from .auth_routes import farmer_response

router = APIRouter(prefix="/farmers", tags=["Farmers"])

@router.get("/{farmer_id}")
def get_farmer(farmer_id:int, db:Session=Depends(get_db)):
    f=db.get(Farmer,farmer_id)
    if not f: raise HTTPException(404,"Farmer not found")
    return farmer_response(f)

@router.patch("/{farmer_id}")
def update_farmer(farmer_id:int,payload:FarmerUpdate,db:Session=Depends(get_db)):
    f=db.get(Farmer,farmer_id)
    if not f: raise HTTPException(404,"Farmer not found")
    for k,v in payload.model_dump(exclude_unset=True).items(): setattr(f,k,v)
    db.commit(); db.refresh(f)
    return farmer_response(f)
