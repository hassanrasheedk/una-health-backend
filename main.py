from fastapi import FastAPI, Depends, Query, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime
from models import Base, GlucoseLevel, SessionLocal, engine
from schemas import GlucoseLevelCreate, GlucoseLevelResponse
import csv
from io import StringIO
import logging

# Initialize the database and FastAPI app
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating tables: {e}")
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/v1/levels/", response_model=List[GlucoseLevelResponse])
def get_glucose_levels(
    user_id: str,
    start: datetime = None,
    stop: datetime = None,
    page: int = Query(1, ge=1),  # ge=1 ensures page number is at least 1
    page_size: int = Query(10, ge=1, le=100),  # Allow max 100 records per request
    sort: Optional[str] = Query("timestamp.desc"),  # Default sorting by timestamp descending
    db: Session = Depends(get_db)):
    """
    Retrieve a list of glucose levels for a given user_id, with optional filtering by start and stop timestamps.
    Supports pagination and sorting.
    """
    query = db.query(GlucoseLevel).filter(GlucoseLevel.user_id == user_id)
    if start:
        query = query.filter(GlucoseLevel.timestamp >= start)
    if stop:
        query = query.filter(GlucoseLevel.timestamp <= stop)
    
    # Sorting logic
    sort_direction = desc if 'desc' in sort else asc
    sort_column = sort.replace('.asc', '').replace('.desc', '')
    if hasattr(GlucoseLevel, sort_column):
        query = query.order_by(sort_direction(getattr(GlucoseLevel, sort_column)))

    # Pagination logic
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    levels = query.all()
    if not levels:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "No glucose levels found for the specified criteria"})
    return levels

@app.get("/api/v1/levels/{id}", response_model=GlucoseLevelResponse)
def get_glucose_level(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific glucose level by its ID.
    """
    glucose_level = db.query(GlucoseLevel).filter(GlucoseLevel.id == id).first()
    if glucose_level is None:
        raise HTTPException(status_code=404, detail="Glucose level not found")
    return glucose_level

@app.post("/api/v1/load-data/")
async def load_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process a CSV file containing glucose data.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file format")
    
    try:
        user_id = file.filename.split('.')[0]  # extracting user_id from the file name
        logger.info(f"Processing file for user_id: {user_id}")
        
        content = await file.read()
        file.file.close()
        
        f = StringIO(content.decode('utf-8'))
        reader = csv.reader(f)
        
        headers = None
        for row in reader:
            if len(row) == 19:
                headers = row
                break
        
        try:
            timestamp_idx = headers.index("Gerätezeitstempel")
            glucose_value_idx = headers.index("Glukosewert-Verlauf mg/dL")
        except ValueError as e:
            logger.error(f"Required columns not found: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Required columns not found in CSV file")
        
        for row in reader:
            timestamp_str = row[timestamp_idx]
            glucose_value_str = row[glucose_value_idx]
            
            if timestamp_str and glucose_value_str:
                try:
                    timestamp = datetime.strptime(timestamp_str, "%d-%m-%Y %H:%M")
                    glucose_value = float(glucose_value_str)
                
                    db_glucose_level = GlucoseLevel(
                        user_id=user_id,
                        timestamp=timestamp,
                        glucose_value=glucose_value,
                    )
                    db.add(db_glucose_level)
                except ValueError as e:
                    logger.error(f"Error parsing row: {row} - {e}")
                    continue
        db.commit()
        logger.info("Data loaded successfully")
        return {"message": "Data loaded successfully"}
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while processing the file")




# bonus endpoints
@app.post("/api/v1/levels/", response_model=GlucoseLevelResponse)
def create_glucose_level(glucose_level: GlucoseLevelCreate, db: Session = Depends(get_db)):
    """
    Create a new glucose level entry.
    """
    try:
        db_glucose_level = GlucoseLevel(**glucose_level.dict())
        db.add(db_glucose_level)
        db.commit()
        db.refresh(db_glucose_level)
        return db_glucose_level
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Failed to create glucose level due to a database integrity error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data integrity error, possibly duplicate data.")
    except Exception as e:
        db.rollback()
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred when trying to create a glucose level.")

@app.get("/api/v1/export-data/", response_class=StreamingResponse)
def export_data(user_id: str, db: Session = Depends(get_db)):
    """
    Export glucose data for a given user_id to a CSV file.
    """
    try:
        query = db.query(GlucoseLevel).filter(GlucoseLevel.user_id == user_id)
        results = query.all()
        if not results:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "No glucose levels found for the specified user ID"})
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "user_id", "timestamp", "glucose_value"])
        for row in results:
            writer.writerow([row.id, row.user_id, row.timestamp, row.glucose_value])
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=glucose_levels_{user_id}.csv"})
    except Exception as e:
        logger.error(f"Failed to export data due to: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Failed to export data due to an internal error"})