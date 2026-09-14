"""
Crop Health System - Backend
Phase 1: Basic FastAPI setup + health-check endpoint

Is file ka kaam sirf itna hai ki FastAPI app create ho aur
verify ho jaye ki server sahi se chal raha hai.

Phase 2+ mein yahan routers (image upload, kindwise, database)
include kiye jayenge. Abhi kuch bhi extra add nahi kiya gaya hai.
"""

from fastapi import FastAPI
from app.routes.upload import router as upload_router
from app.routes.analyze import router as analyze_router

app = FastAPI(
    title="Crop Health System - Backend",
    description="AI Disease Detection + Image Upload API + Disease Analysis module",
    version="0.1.0",
)
app.include_router(upload_router, prefix="/api")
app.include_router(analyze_router)

@app.get("/")
def health_check():
    """
    Simple health-check endpoint.
    Ye sirf confirm karta hai ki server up hai aur running hai.
    """
    return {
        "status": "ok",
        "message": "Crop Health System backend is running (Phase 1)",
    }
