import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./database.db"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

# Read settings from environment / .env file
settings = Settings()

# Check if we are using SQLite and apply the required check_same_thread argument
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
