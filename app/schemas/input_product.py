"""
Input Product schemas.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class InputProductBase(BaseModel):
    name: str = Field(..., example="Improved Maize Seed")
    category: Optional[str] = Field(None, example="seed")
    price: Optional[str] = Field(None, example="5.50")


class InputProductCreate(InputProductBase):
    pass


class InputProductResponse(InputProductBase):
    id: str = Field(..., example="prod_123")

    model_config = ConfigDict(from_attributes=True)