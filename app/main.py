from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import io
import logging

# --- PostgreSQL Configuration ---
DATABASE_URL = "postgresql://globant_user:globant_pass@localhost:5432/globant_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()