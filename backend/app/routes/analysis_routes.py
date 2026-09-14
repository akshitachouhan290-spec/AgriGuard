import json, os, base64
import httpx
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Farmer, Field, DiseaseAnalysis
from ..utils import today_label
router=APIRouter(prefix="/analyze",tags=["Analysis"])

def mock_result(crop):
    c=(crop or "").lower()
    if c=="tomato": return ("Early Blight",91,"High","Moderate",["Target-like brown lesions detected","High humidity can accelerate fungal spread","Pattern is consistent with early blight"],["Remove infected leaves","Avoid overhead irrigation","Use locally approved fungicide if advised"])
    if c=="potato": return ("Late Blight",88,"High","Severe",["Water-soaked dark lesions are consistent with late blight","Wet conditions increase spread"],["Remove diseased foliage","Protect mature tubers from infection"])
    if c=="wheat": return ("Yellow Rust",85,"Medium","Mild",["Yellow pustules can match rust symptoms"],["Monitor nearby plants","Use locally recommended treatment if spread increases"])
    if c=="rice": return ("Blast Disease",90,"High","Severe",["Spindle-shaped lesions can indicate blast","Leaf wetness increases disease pressure"],["Avoid excess nitrogen","Remove heavily infected residue"])
    return ("Healthy Leaf",96,"Low","None",["No major anomaly was detected by the demo classifier"],["Continue regular monitoring","Maintain good field hygiene"])

async def plant_id(image_bytes):
    key=os.getenv("PLANT_ID_API_KEY")
    if not key: return None
    payload={"images":[base64.b64encode(image_bytes).decode("ascii")],"health":"only"}
    async with httpx.AsyncClient(timeout=30) as client:
        r=await client.post("https://api.plant.id/v3/identification",headers={"Api-Key":key},json=payload)
    if r.status_code not in (200,201): raise HTTPException(502,f"Plant.id returned HTTP {r.status_code}")
    data=r.json(); result=data.get("result",{})
    healthy=result.get("is_healthy",{}).get("binary")
    ds=result.get("disease",{}).get("suggestions",[])
    if healthy and not ds: return ("Healthy Leaf",round(result.get("is_healthy",{}).get("probability",0.96)*100,2),"Low","None",["Plant.id marked the plant as healthy"],["Continue regular monitoring"])
    d=ds[0] if ds else {}
    conf=round(float(d.get("probability",0))*100,2)
    return (d.get("name") or "Unknown",conf,"High" if conf>=80 else "Medium" if conf>=60 else "Low","Severe" if conf>=90 else "Moderate",["Plant.id health assessment returned this leading suggestion"],["Follow local agricultural guidance and monitor progression"])

@router.post("/")
async def analyze(farmer_id:int=Form(...),field_id:int=Form(...),crop:str=Form(""),file:UploadFile=File(...),db:Session=Depends(get_db)):
    farmer=db.get(Farmer,farmer_id); field=db.get(Field,field_id)
    if not farmer: raise HTTPException(404,"Farmer not found")
    if not field: raise HTTPException(404,"Field not found")
    if field.farmer_id!=farmer_id: raise HTTPException(400,"Field does not belong to farmer")
    if not file.content_type or not file.content_type.startswith("image/"): raise HTTPException(400,"Please upload an image")
    raw=await file.read()
    if not raw: raise HTTPException(400,"Uploaded image is empty")
    crop=crop or (field.crop.name if field.crop else "Tomato")
    result=await plant_id(raw) if os.getenv("PLANT_ID_API_KEY") else None
    disease,confidence,risk,severity,why,advice=result or mock_result(crop)
    status="auto_confirmed" if confidence>=70 else "needs_review"
    a=DiseaseAnalysis(farmer_id=farmer_id,field_id=field_id,image_ref=file.filename or "",crop=crop,disease=disease,
                      confidence=confidence,severity=severity,risk=risk,why_json=json.dumps(why),advice_json=json.dumps(advice),status=status)
    db.add(a)
    field.last_analysis=today_label(); field.current_risk=risk; field.disease_detected=disease; field.severity=severity
    db.commit(); db.refresh(a)
    return {"id":a.id,"date":today_label(),"crop":crop,"disease":disease,"confidence":confidence,"risk":risk,
            "severity":severity,"why":why,"advice":advice,"status":status,"filename":file.filename}

@router.get("/history/{farmer_id}")
def history(farmer_id:int,db:Session=Depends(get_db)):
    rows=db.query(DiseaseAnalysis).filter(DiseaseAnalysis.farmer_id==farmer_id).order_by(DiseaseAnalysis.created_at.desc()).all()
    return [{"id":a.id,"date":a.created_at.strftime("%d %b"),"crop":a.crop,"disease":a.disease,"confidence":a.confidence,
             "risk":a.risk,"severity":a.severity,"why":json.loads(a.why_json or "[]"),"advice":json.loads(a.advice_json or "[]"),
             "status":a.status} for a in rows]
