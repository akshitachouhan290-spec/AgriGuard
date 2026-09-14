from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import Farmer, Crop, Field
from .security import hash_password
from .routes import auth_routes, farmer_routes, field_routes, crop_routes, analysis_routes, system_routes

Base.metadata.create_all(bind=engine)

app=FastAPI(title="Crop Health System API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(auth_routes.router)
app.include_router(farmer_routes.router)
app.include_router(field_routes.router)
app.include_router(crop_routes.router)
app.include_router(analysis_routes.router)
app.include_router(system_routes.router,prefix="/api")

@app.get("/")
def root(): return {"status":"ok","message":"Crop Health System backend is running","docs":"/docs"}

def seed():
    db=SessionLocal()
    try:
        crops=["Tomato","Potato","Wheat","Rice","Maize","Cotton","Sugarcane","Onion","Chilli","Soybean","Groundnut","Mustard","Barley","Pea","Gram","Lentil","Mango","Apple","Banana","Grapes","Pomegranate","Okra","Cabbage","Brinjal","Cauliflower","Carrot","Cucumber","Peanut"]
        for name in crops:
            if not db.query(Crop).filter(Crop.name==name).first(): db.add(Crop(name=name,category="Field/Horticulture"))
        if not db.query(Farmer).filter(Farmer.id==1).first():
            f=Farmer(id=1,name="Farmer Rajesh",phone="9999999999",language="Hindi",village="Jaipur",district="Jaipur",state="Rajasthan",latitude=26.9124,longitude=75.7873,password_hash=hash_password("demo123"))
            db.add(f); db.flush()
        db.commit()
        if not db.query(Field).filter(Field.farmer_id==1).first():
            tomato=db.query(Crop).filter(Crop.name=="Tomato").first()
            wheat=db.query(Crop).filter(Crop.name=="Wheat").first()
            db.add_all([Field(farmer_id=1,field_name="North Tomato Field",crop_id=tomato.id,area=2.5,latitude=26.9124,longitude=75.7873,location_label="Jaipur, Rajasthan"),
                        Field(farmer_id=1,field_name="East Wheat Field",crop_id=wheat.id,area=3.0,latitude=26.9124,longitude=75.7873,location_label="Jaipur, Rajasthan")])
            db.commit()
    finally: db.close()

seed()
