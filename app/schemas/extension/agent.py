"""Agent schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentBase(BaseModel):
    agent_id: str = Field(..., examples=["AG001"])
    name: str = Field(..., examples=["John Doe"])
    phone: Optional[str] = Field(None, examples=["+254700000000"])
    email: Optional[str] = Field(None, examples=["john@example.com"])
    assigned_ward: Optional[str] = Field(None, examples=["W001"])
    is_active: Optional[str] = Field("Active", examples=["Active"])


class AgentCreate(AgentBase):
    pass


class AgentResponse(AgentBase):
    id: str = Field(..., examples=["agent_123"])
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True