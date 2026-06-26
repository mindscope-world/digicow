"""Input Request Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InputRequestBase(BaseModel):
    farmer_id: str = Field(..., examples=["DC00001"])
    product_id: str = Field(..., examples=["prod_123"])
    quantity_requested: int = Field(..., gt=0, examples=[5])
    notes: Optional[str] = Field(None, examples=["Farmer needs urgent supply"])


class InputRequestCreate(InputRequestBase):
    pass


class InputRequestResponse(InputRequestBase):
    id: str = Field(..., examples=["req_abc123"])
    status: str = Field(..., examples=["pending"])
    quantity_approved: int = Field(default=0)
    date_requested: datetime
    date_fulfilled: Optional[datetime] = None

    class Config:
        from_attributes = True