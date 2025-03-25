from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import pandas as pd
import io
import logging
from database import SessionLocal, engine
from models import Base, Department, Job, HiredEmployee

# Initialize tables before app starts
Base.metadata.create_all(bind=engine)

app = FastAPI()
logger = logging.getLogger(__name__)

# Table configurations
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

def validate_data(df: pd.DataFrame, table_name: str):
    config = TABLE_CONFIG.get(table_name)
    if not config:
        raise ValueError("Invalid table name")
    
    if len(df.columns) != len(config["columns"]):
        raise ValueError(f"Expected {len(config['columns'])} columns, got {len(df.columns)}")

    if df.isnull().values.any():
        raise ValueError("CSV contains null values")

    if not pd.api.types.is_integer_dtype(df["id"]):
        raise ValueError("ID column must contain integers")

@app.post("/upload/{table_name}")
async def upload_csv(
    table_name: str,
    file: UploadFile = File(...),
    batch_size: int = 1000
):
    if not 1 <= batch_size <= 1000:
        return JSONResponse(
            status_code=400,
            content={"message": "Batch size must be between 1 and 1000"}
        )

    config = TABLE_CONFIG.get(table_name)
    if not config:
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid table name"}
        )

    try:
        contents = await file.read()
        df = pd.read_csv(
            io.StringIO(contents.decode('utf-8')),
            header=None,
            names=config["columns"]

        )
    except Exception as e:
        logger.error(f"CSV Error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"message": f"CSV Error: {str(e)}"}
        )

    try:
        validate_data(df, table_name)
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"message": str(e)}
        )

    db = SessionLocal()
    total_inserted = 0
    try:
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            try:
                db.bulk_insert_mappings(config["model"], batch.to_dict(orient='records'))
                db.commit()
                total_inserted += len(batch)
            except Exception as e:
                db.rollback()
                logger.error(f"Database Error: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"message": f"Database Error: {str(e)}"}
                )
        return JSONResponse(
            status_code=200,
            content={
                "message": "Data uploaded successfully",
                "total_records": len(df),
                "inserted_records": total_inserted,
                "batches_used": (len(df) // batch_size) + 1
            }
        )
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)