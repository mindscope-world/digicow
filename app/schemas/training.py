"""
Training Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TrainingSessionBase(BaseModel):
    title: str = Field(..., example="Soil Health Management")
    description: Optional[str] = Field(None, example="Learn about soil testing and amendment")
    session_date: datetime = Field(..., example="2023-06-15T10:00:00Z")
    location: Optional[str] = Field(None, example="Nairobi Farmers Training Center")
    trainer_ids: List[str] = Field(default_factory=list, example=["TRN001", "TRN002"])
    topic_ids: List[str] = Field(default_factory=list, example=["Soil Testing", "Composting"])


class TrainingSessionCreate(TrainingSessionBase):
    pass


class TrainingSessionResponse(TrainingSessionBase):
    id: str
    # We'll add related data as needed for the detail view
    conducted_by: List[str] = []  # Trainer names
    covers: List[str] = []  # Topic titles
    participated_in: List[str] = []  # Farmer IDs who participated

    class Config:
        from_attributes = True