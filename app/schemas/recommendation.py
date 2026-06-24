"""
Recommendation schemas for advisory system.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AdvisoryRecommendationBase(BaseModel):
    recommendation_type: str = Field(..., example="spraying")
    advice: str = Field(..., example="Apply pesticide X after rainfall")
    date_given: datetime = Field(default_factory=datetime.utcnow)
    priority: str = Field(..., example="medium")


class AdvisoryRecommendationResponse(AdvisoryRecommendationBase):
    id: str = Field(..., example="rec_123")
    farmer_id: Optional[str] = Field(None, example="DC00001")

    class Config:
        orm_mode = True


class TrendingTopic(BaseModel):
    topic: str = Field(..., example="Disease prevention")
    frequency: int = Field(..., example=15)
    region: Optional[str] = Field(None, example="Central Ward")


class RecommendationGenerateResponse(BaseModel):
    message: str = Field(..., example="Recommendations generated successfully")
    count: int = Field(..., example=42)