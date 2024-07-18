from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./prod.db"

Base = declarative_base()

class GlucoseLevel(Base):
    """
    GlucoseLevel model for storing glucose level data.
    
    Attributes:
        id (int): Primary key, auto-incremented.
        user_id (str): ID of the user.
        timestamp (datetime): Timestamp of the glucose level measurement.
        glucose_value (float): Value of the glucose level.
    """
    __tablename__ = 'glucose_levels'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    timestamp = Column(DateTime)
    glucose_value = Column(Float)


# Create the SQLite database engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating tables: {e}")
