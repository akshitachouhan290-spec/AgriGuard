from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Crop
router=APIRouter(prefix="/crops",tags=["Crops"])
@router.get("/")
def list_crops(db:Session=Depends(get_db)):
    return [{"id":c.id,"name":c.name,"category":c.category} for c in db.query(Crop).order_by(Crop.name).all()]
