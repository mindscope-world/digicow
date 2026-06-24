"""
Adoption Endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from app.schemas.adoption import AdoptionCreate, AdoptionResponse
from app.services.adoption_service import AdoptionService

router = APIRouter()


@router.post("/", response_model=AdoptionResponse, status_code=status.HTTP_201_CREATED)
async def record_adoption(adoption: AdoptionCreate):
    """
    Record a new input adoption
    """
    try:
        return await AdoptionService.create_adoption(adoption)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )