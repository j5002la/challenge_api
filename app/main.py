from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import pandas as pd
import io
import logging
from datetime import datetime
from database import SessionLocal, engine
from models import Base, Department, Job, HiredEmployee

# Initialize tables before app starts
Base.metadata.create_all(bind=engine)

app = FastAPI()
logger = logging.getLogger(__name__)

# Table configurations (without dtypes)
TABLE_CONFIG = {
    "departments": {
        "columns": ["id", "department"],
        "model": Department
    },
    "jobs": {
        "columns": ["id", "job"],
        "model": Job
    },
    "hired_employees": {
        "columns": ["id", "name", "datetime", "department_id", "job_id"],
        "model": HiredEmployee
    }
}

def clean_data(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Clean data by replacing empty/missing values with None"""
    # Convert empty strings to None
    df = df.replace(r'^\s*$', None, regex=True)
    
    # Handle datetime conversion
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(
            df['datetime'], 
            errors='coerce', 
            format='%Y-%m-%dT%H:%M:%SZ'
        )
    
    # Convert numeric columns to numbers
    for col in df.columns:
        if col.endswith('_id') or col == 'id':
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Explicit replacement of all NaN/NaT values with None
    df = df.applymap(lambda x: None if pd.isna(x) else x)
    
    return df

@app.post("/upload/{table_name}")
async def upload_csv(
    table_name: str,
    file: UploadFile = File(...),
    batch_size: int = 1000
):
    if table_name not in TABLE_CONFIG:
        raise HTTPException(status_code=400, detail="Invalid table name")

    if not 1 <= batch_size <= 1000:
        raise HTTPException(status_code=400, detail="Batch size must be 1-1000")

    try:
        # Read CSV as strings to preserve raw data
        contents = await file.read()
        df = pd.read_csv(
            io.StringIO(contents.decode('utf-8')),
            header=None,
            names=TABLE_CONFIG[table_name]["columns"],
            dtype=str,
            keep_default_na=False
        )
    except Exception as e:
        logger.error(f"CSV read error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"CSV parsing error: {str(e)}")

    db = SessionLocal()
    try:
        # Clean data
        df = clean_data(df, table_name)
        
        # Convert to records
        records = df.to_dict(orient='records')
        
        # Batch insert
        total_inserted = 0
        for i in range(0, len(records), batch_size):
            try:
                db.bulk_insert_mappings(
                    TABLE_CONFIG[table_name]["model"], 
                    records[i:i+batch_size]
                )
                db.commit()
                total_inserted += len(records[i:i+batch_size])
            except Exception as e:
                db.rollback()
                logger.error(f"Database error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Batch insert failed: {str(e)}")

        return {
            "message": "Upload successful",
            "received": len(df),
            "inserted": total_inserted,
            "failed": len(df) - total_inserted
        }

    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)