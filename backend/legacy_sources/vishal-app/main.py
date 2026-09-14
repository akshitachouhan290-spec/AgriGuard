from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth_routes

# Initialize database tables on startup
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Crop Disease Detection & Farmer Assistance System - Authentication API",
    description=(
        "Standalone authentication microservice. Handles farmer registration, "
        "login verification, profile management, and JWT generation & verification."
    ),
    version="1.0.0",
)

# Enable CORS for cross-origin frontend requests (e.g., React, Vue, mobile apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for integration flexibility; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_routes.router)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Crop Disease Detection & Farmer Assistance System - Authentication API is running.",
        "docs_url": "/docs"
    }
