"""Agent schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentBase(BaseModel):
    agent_id: str = Field(..., example="AG001")
    name: str = Field(..., example="John Doe")
    phone: Optional[str] = Field(None, example="+254700000000")
    email: Optional[str] = Field(None, example="john@example.com")
    assigned_ward: Optional[str] = Field(None, example="W001")
    is_active: Optional[str] = Field("Active", example="Active")


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    id: str = Field(..., example="agent_123")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True