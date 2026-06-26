"""
Recommendation schemas for advisory system.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AdvisoryRecommendationBase(BaseModel):
    recommendation_type: str = Field(..., examples=["spraying"])
    advice: str = Field(..., examples=["Apply pesticide X after rainfall"])
    date_given: datetime = Field(default_factory=datetime.utcnow)
    priority: str = Field(..., examples=["medium"])


class AdvisoryRecommendationResponse(AdvisoryRecommendationBase):
    id: str = Field(..., examples=["rec_123"])
    farmer_id: Optional[str] = Field(None, examples=["DC00001"])

    class Config:
        from_attributes = True


class TrendingTopic(BaseModel):
    topic: str = Field(..., examples=["Disease prevention"])
    frequency: int = Field(..., examples=[15])
    region: Optional[str] = Field(None, examples=["Central Ward"])


class RecommendationGenerateResponse(BaseModel):
    message: str = Field(..., examples=["Recommendations generated successfully"])
    count: int = Field(..., examples=[42])