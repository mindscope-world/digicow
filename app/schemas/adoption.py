"""
Adoption Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AdoptionBase(BaseModel):
    farmer_id: str = Field(..., example="DC00001")
    input_product_name: str = Field(..., example="Seed Type A")


class AdoptionCreate(AdoptionBase):
    pass


class AdoptionResponse(AdoptionBase):
    id: str = Field(alias="uid")
    date_adopted: datetime

    class Config:
        from_attributes = True