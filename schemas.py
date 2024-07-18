from pydantic import BaseModel
from datetime import datetime

class GlucoseLevelCreate(BaseModel):
    """
    Schema for creating a new glucose level entry.
    
    Attributes:
        user_id (str): The ID of the user to whom the glucose level belongs.
        timestamp (datetime): The timestamp of the glucose level measurement.
        glucose_value (float): The value of the glucose level.
    """
    user_id: str
    timestamp: datetime
    glucose_value: float

class GlucoseLevelResponse(GlucoseLevelCreate):
    """
    Schema for the response of a glucose level entry.
    
    Inherits from GlucoseLevelCreate and adds:
    Attributes:
        id (int): The ID of the glucose level entry.
    """
    id: int

    class Config:
        """
        Configuration for Pydantic model.
        """
        orm_mode = True
