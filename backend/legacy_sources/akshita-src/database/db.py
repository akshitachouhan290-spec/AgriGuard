import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv


load_dotenv()

# Reads the connection string from .env — never hardcode credentials here. if .env exists → use Supabase PostgreSQL, otherwise → use local PostgreSQL
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://postgres:postgres@localhost:5432/crop_health_db",
# )

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    if engine.dialect.name == "sqlite":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db():
    """
    Used as a FastAPI dependency. Opens one DB session per request
    and always closes it, even if an error happens mid-request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()