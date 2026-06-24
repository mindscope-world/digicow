"""Analytics Endpoints"""
from typing import List, Dict, Any
from fastapi import APIRouter
from app.services.analytics_service import analytics_service

router = APIRouter()


@router.get("/adoption-rates", response_model=List[dict])
async def get_adoption_rates():
    """
    Get adoption rates by product
    """
    return await analytics_service.get_adoption_rates()


@router.get("/trainer-effectiveness", response_model=List[dict])
async def get_trainer_effectiveness():
    """
    Get trainer performance metrics
    """
    return await analytics_service.get_trainer_effectiveness()


@router.get("/ward-performance", response_model=List[dict])
async def get_ward_performance():
    """
    Get performance metrics by ward
    """
    return await analytics_service.get_ward_performance()


@router.get("/trends", response_model=dict)
async def get_trends():
    """
    Get temporal trends in adoption and training
    """
    return await analytics_service.get_trends()