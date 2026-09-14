from fastapi import APIRouter, Depends, Query
from ..database import get_db
from ..models import Farmer, Field, DiseaseAnalysis
from ..schemas import ChatRequest
router=APIRouter(tags=["System"])

@router.get("/weather")
def weather(lat:float=26.9124,lon:float=75.7873):
    # Stable fallback data; frontend remains functional without a weather API key.
    return {"temp":29,"feelsLike":31,"humidity":72,"rainProbability":42,"windSpeed":11,"condition":"Partly cloudy","latitude":lat,"longitude":lon}

@router.get("/alerts/{farmer_id}")
def alerts(farmer_id:int,db=Depends(get_db)):
    rows=db.query(DiseaseAnalysis).filter(DiseaseAnalysis.farmer_id==farmer_id,DiseaseAnalysis.risk=="High").order_by(DiseaseAnalysis.created_at.desc()).limit(20).all()
    return [{"id":a.id,"title":"🚨 HIGH RISK","message":f"Possible {a.disease} detected in your {a.crop} field.","fieldId":a.field_id,"type":"disease","date":a.created_at.strftime("%d %b")} for a in rows]

@router.get("/risk/{field_id}")
def risk(field_id:int,db=Depends(get_db)):
    f=db.get(Field,field_id)
    if not f: return {"crop":"Unknown","disease":"Unknown","risk":"Low","score":0,"summary":"No field found."}
    score={"High":78,"Medium":45,"Low":15}.get(f.current_risk,15)
    return {"crop":f.crop.name if f.crop else "Unknown","disease":f.disease_detected,"risk":f.current_risk,"score":score,
            "summary":"Weather and crop conditions may increase disease spread." if f.current_risk!="Low" else "Conditions are stable. Low chance of disease multiplication."}

@router.post("/chat")
def chat(payload:ChatRequest,db=Depends(get_db)):
    text=payload.message.strip().lower()
    if "latest crop report" in text:
        a=db.query(DiseaseAnalysis).order_by(DiseaseAnalysis.created_at.desc()).first()
        if a: return {"text":f"Latest report: {a.crop} — {a.disease}, {a.confidence:.0f}% confidence, {a.severity} severity, {a.risk} risk."}
    if "what is wrong" in text: return {"text":"Upload a clear crop photo using Check My Crop and I will run the health analysis."}
    if "risk" in text: return {"text":"I calculate crop risk from the latest field analysis and environmental conditions."}
    return {"text":"I can help with crop health, disease reports, field risk and practical crop-care guidance."}
