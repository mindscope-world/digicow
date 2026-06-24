"""Visit Log schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VisitLogBase(BaseModel):
    farmer_id: str = Field(..., example="DC00001")
    purpose: str = Field(..., example="Follow-up on adoption")
    notes: Optional[str] = Field(None, explanation="Free-form notes from the visit")
    agent_id: Optional[str] = Field(None, example="AG001", description="ID of the agent who conducted the visit")


class VisitLogCreate(VisitLogBase):
    pass


class VisitLogResponse(VisitLogBase):
    id: str = Field(..., example="visit_123")
    visit_date: datetime

    class Config:
        orm_mode = True