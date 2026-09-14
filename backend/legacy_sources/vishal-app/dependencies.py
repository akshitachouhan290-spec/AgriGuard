from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from app.database import SessionLocal, settings
from app.models import Farmer

# Setup OAuth2 Bearer Token Extraction Scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    description="Bearer token authentication. Enter your token in the format: Bearer <JWT_TOKEN>"
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that yields a local database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_farmer(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Farmer:
    """
    Reusable dependency to retrieve the currently logged-in farmer.
    Validates JWT signature, checks expiration, and queries the database for the user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token using the settings configured algorithms and secret key
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract the subject (farmer/user ID)
        farmer_id: str = payload.get("sub")
        if farmer_id is None:
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    # Query database to check if farmer still exists
    farmer = db.query(Farmer).filter(Farmer.id == int(farmer_id)).first()
    if farmer is None:
        raise credentials_exception
        
    return farmer
