"""Demand Forecast schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DemandForecastItem(BaseModel):
    product_id: str = Field(..., example="prod_123")
    product_name: str = Field(..., example="Improved Maize Seed")
    forecasted_quantity: float = Field(..., example=125.5)
    confidence: float = Field(..., example=0.85, ge=0, le=1)
    # optional: time period
    period: str = Field(..., example="2025-02")  # YYYY-MM


class DemandForecastResponse(BaseModel):
    ward_id: str = Field(..., example="W001")
    forecast: List[DemandForecastItem]
    generated_at: datetime

    class Config:
        orm_mode = True