"""
Farmer Management Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse, FarmerProfileResponse
from app.schemas.adoption import AdoptionResponse
from app.services.farmer_service import FarmerService
from app.services.adoption_service import AdoptionService

router = APIRouter()


@router.get("/", response_model=List[FarmerResponse])
async def list_farmers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    gender: Optional[str] = None,
    age_bracket: Optional[str] = None,
    registration_method: Optional[str] = None,
    belongs_to_cooperative: Optional[bool] = None,
    min_engagement_score: Optional[int] = None,
    status: Optional[str] = None,
):
    """
    List farmers with filtering, pagination, and scoring
    """
    # For now, we'll ignore some filters that aren't implemented in the service yet
    # In a full implementation, these would be passed to the service
    farmers = await FarmerService.get_farmers(
        skip=skip,
        limit=limit,
        gender=gender,
        age_bracket=age_bracket,
        status=status
    )

    # Apply additional filters that aren't handled by the service yet
    if registration_method is not None:
        # This would be implemented in the service in a full implementation
        pass

    if belongs_to_cooperative is not None:
        # This would be implemented in the service in a full implementation
        pass

    if min_engagement_score is not None:
        # This would be implemented in the service in a full implementation
        pass

    return farmers


@router.get("/{farmer_id}", response_model=FarmerProfileResponse)
async def get_farmer(farmer_id: str = Path(..., examples=["DC00001"], description="The ID of the farmer")):
    """
    Get detailed farmer profile with relationships
    """
    farmer = await FarmerService.get_farmer_profile_with_relationships(farmer_id)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    return farmer


@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer(farmer: FarmerCreate):
    """
    Register new farmer
    """
    try:
        return await FarmerService.create_farmer(farmer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{farmer_id}", response_model=FarmerResponse)
async def update_farmer(farmer_update: FarmerUpdate, farmer_id: str = Path(..., examples=["DC00001"], description="The ID of the farmer")):
    """
    Update farmer information
    """
    farmer = await FarmerService.update_farmer(farmer_id, farmer_update)
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    return farmer


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_farmer(farmer_id: str = Path(..., examples=["DC00001"], description="The ID of the farmer")):
    """
    Deactivate farmer record (soft delete)
    """
    success = await FarmerService.deactivate_farmer(farmer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farmer with ID {farmer_id} not found"
        )
    return None


@router.get("/{farmer_id}/adoption-history", response_model=List[AdoptionResponse])
async def get_adoption_history(
    farmer_id: str = Path(..., examples=["DC00001"], description="The ID of the farmer")
):
    """
    Get adoption timeline for a specific farmer
    """
    adoptions = await AdoptionService.get_farmer_adoption_history(farmer_id)
    return adoptions