"""Demand Forecast schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DemandForecastItem(BaseModel):
    product_id: str = Field(..., examples=["prod_123"])
    product_name: str = Field(..., examples=["Improved Maize Seed"])
    forecasted_quantity: float = Field(..., examples=[125.5])
    confidence: float = Field(..., examples=[0.85], ge=0, le=1)
    # optional: time period
    period: str = Field(..., examples=["2025-02"])  # YYYY-MM


class DemandForecastResponse(BaseModel):
    ward_id: str = Field(..., examples=["W001"])
    forecast: List[DemandForecastItem]
    generated_at: datetime

    class Config:
        from_attributes = True