"""
Training Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.schemas.training import TrainingSessionCreate, TrainingSessionResponse
from app.services.training_service import TrainingService

router = APIRouter()


@router.post("/", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_training_session(training: TrainingSessionCreate):
    """
    Record a new training session
    """
    return await TrainingService.create_training_session(training)


@router.get("/{session_id}", response_model=TrainingSessionResponse)
async def get_training_session(
    session_id: str = Path(..., examples=["00000000-0000-0000-0000-000000000000"], description="The element ID of the training session")
):
    """
    Get training session details by ID
    """
    training = await TrainingService.get_training_session(session_id)
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training session with ID {session_id} not found"
        )
    return training


@router.get("/", response_model=List[TrainingSessionResponse])
async def list_training_sessions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    title: Optional[str] = Query(None, description="Filter by title (case-insensitive partial match)"),
    location: Optional[str] = Query(None, description="Filter by location (case-insensitive partial match)"),
    start_date: Optional[str] = Query(None, description="Filter by start date (inclusive, ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (inclusive, ISO format)")
):
    """
    List training sessions with filtering and pagination
    """
    # Convert date strings to datetime objects if provided
    from datetime import datetime
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    trainings = await TrainingService.list_training_sessions(
        skip=skip,
        limit=limit,
        title=title,
        location=location,
        start_date=start_dt,
        end_date=end_dt
    )
    return trainings