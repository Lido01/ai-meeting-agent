import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session


# Load variables from the .env file
load_dotenv()


# Get the PostgreSQL connection URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")


# Create the connection/engine between FastAPI and PostgreSQL
# SQLAlchemy uses this engine to communicate with the database.
engine = create_engine(DATABASE_URL)


# Create a database session factory
# Each API request can create a session using SessionLocal().
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for all our database models
# User, Meeting, and Task will inherit from this Base.
Base = declarative_base()


# Provides a database session to our API routes.
def get_db():
    db = SessionLocal()

    try:
        # Give the API route access to the database
        yield db

    finally:
        db.close()