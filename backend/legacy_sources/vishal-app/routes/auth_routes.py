from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_farmer
from app.models import Farmer
from app.schemas import FarmerRegister, FarmerLogin, FarmerResponse, Token
from app.auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register", 
    status_code=status.HTTP_201_CREATED,
    response_model=FarmerResponse,
    summary="Register a new farmer",
    description="Validates farmer details, checks for duplicate mobile numbers, hashes the password, and saves the record in SQLite."
)
def register_farmer(
    payload: FarmerRegister, 
    db: Session = Depends(get_db)
):
    # Check if the mobile/phone number already exists
    existing_farmer = db.query(Farmer).filter(Farmer.phone == payload.phone).first()
    if existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
        
    # Hash password before storing
    hashed_password = get_password_hash(payload.password)
    
    # Instantiate the Farmer model mapped from schemas
    new_farmer = Farmer(
        name=payload.name,
        phone=payload.phone,
        language=payload.language,
        village=payload.village,
        district=payload.district,
        state=payload.state,
        latitude=payload.latitude,
        longitude=payload.longitude,
        main_crop=payload.main_crop,
        field_size=payload.field_size,
        password_hash=hashed_password
    )
    
    db.add(new_farmer)
    db.commit()
    db.refresh(new_farmer)
    return new_farmer

@router.post(
    "/login", 
    response_model=Token,
    summary="Login as a farmer",
    description="Validates credentials and generates a standard JWT access token."
)
def login_farmer(
    payload: FarmerLogin, 
    db: Session = Depends(get_db)
):
    # Find farmer by phone/mobile
    farmer = db.query(Farmer).filter(Farmer.phone == payload.phone).first()
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Verify hashed password
    if not verify_password(payload.password, farmer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generate token payload containing user ID (sub)
    token_payload = {"sub": str(farmer.id)}
    access_token = create_access_token(data=token_payload)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get(
    "/profile", 
    response_model=FarmerResponse,
    summary="Get authenticated farmer profile",
    description="Returns the profile details of the logged-in farmer. Requires a valid JWT token."
)
def get_profile(current_farmer: Farmer = Depends(get_current_farmer)):
    # Returns the farmer associated with the valid JWT.
    # This prevents access to other farmers' profiles.
    return current_farmer

@router.post(
    "/logout",
    summary="Log out of the system",
    description="Because JWT is stateless, the server cannot invalidate the token directly. The client should discard the token from local storage."
)
def logout():
    return {
        "message": "Successfully logged out. Please discard your JWT token client-side."
    }
