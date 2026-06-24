"""Analytics schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AdoptionRateItem(BaseModel):
    product: str
    adoption_count: int
    unique_farmers: int
    adoption_rate: float  # percentage


class TrainerMetric(BaseModel):
    trainer_id: str
    trainer_name: str
    trainings_conducted: int
    average_rating: float
    feedback_score: float


class WardMetric(BaseModel):
    ward_id: str
    ward_name: str
    farmer_count: int
    adoption_count: int
    training_participation: int
    performance_score: float


class TrendPoint(BaseModel):
    period: str  # e.g., "2024-01"
    adoption_count: int
    training_count: int


class TrendsResponse(BaseModel):
    adoption_trend: List[TrendPoint]
    training_trend: List[TrendPoint]


# Response models for endpoints
class AdoptionRatesResponse(BaseModel):
    data: List[AdoptionRateItem]


class TrainerEffectivenessResponse(BaseModel):
    data: List[TrainerMetric]


class WardPerformanceResponse(BaseModel):
    data: List[WardMetric]


class AnalyticsTrendsResponse(BaseModel):
    data: TrendsResponse