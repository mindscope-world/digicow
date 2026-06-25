"""
Recommendation Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.services.recommendation_service import recommendation_service
from app.schemas.recommendation import (
    AdvisoryRecommendationResponse,
    TrendingTopic,
    RecommendationGenerateResponse,
)

router = APIRouter()


@router.get("/farmer/{farmer_id}", response_model=List[AdvisoryRecommendationResponse])
async def get_farmer_recommendations(
    farmer_id: str = Path(..., examples=["DC00001"], description="The ID of the farmer")
):
    """
    Get personalized recommendations for a specific farmer.
    """
    # In a real app, we would fetch the farmer to ensure existence.
    # For simplicity, we pass a dummy farmer object to service.
    # TODO: Implement proper farmer lookup.
    from app.models.farmer import Farmer

    farmer = Farmer.get_by_id(farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found",
        )
    recommendations = await recommendation_service.get_farmer_recommendations(farmer)
    return recommendations


@router.get("/ward/{ward_id}", response_model=List[AdvisoryRecommendationResponse])
async def get_ward_recommendations(
    ward_id: str = Path(..., examples=["W001"], description="The ID of the ward")
):
    """
    Get ward-level recommendations.
    """
    # Optionally validate ward exists
    from app.models.location.ward import Ward

    ward = Ward.get_by_code(ward_id)  # Assuming ward_id is code; adjust if needed
    if not ward:
        # Still return empty list or 404? We'll return empty list for now.
        pass
    recommendations = await recommendation_service.get_ward_recommendations(ward_id)
    return recommendations


@router.post("/generate", response_model=RecommendationGenerateResponse, status_code=status.HTTP_200_OK)
async def generate_recommendations():
    """
    Trigger recommendation generation (e.g., run ML model or batch job).
    """
    result = await recommendation_service.generate_recommendations()
    return result


@router.get("/trending-topics", response_model=List[TrendingTopic])
async def get_trending_topics(
    region: Optional[str] = Query(None, description="Filter by region/ward code")
):
    """
    Get trending training topics by region (or globally).
    """
    topics = await recommendation_service.get_trending_topics(region)
    return topics