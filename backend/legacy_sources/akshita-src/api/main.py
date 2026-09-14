from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import farmer_routes, field_routes, disease_routes, crop_routes

app = FastAPI(title="Crop Health system")

# Allows the frontend (running on a different port/domain) to call this backend.
# Tighten allow_origins to your actual frontend URL before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farmer_routes.router)
app.include_router(field_routes.router)
app.include_router(disease_routes.router)
app.include_router(crop_routes.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Crop Health Advisory backend is running"}