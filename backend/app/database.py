import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create connection between FastAPI and PostgreSQL
engine = create_engine(DATABASE_URL)

# Test the connection
with engine.connect() as connection:
    print("Database connected successfully!")