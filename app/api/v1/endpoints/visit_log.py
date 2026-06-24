"""Visit Log Endpoints"""
from fastapi import APIRouter, HTTPException, Path, status
from app.services.visit_log_service import visit_log_service
from app.schemas.extension.visit_log import VisitLogCreate, VisitLogResponse
from typing import List

# Router for creating visit logs
router_log = APIRouter(prefix="/visit-logs", tags=["visit-logs"])

# Router for retrieving visit history
router_history = APIRouter(prefix="/visit-history", tags=["visit-history"])


@router_log.post("/", response_model=VisitLogResponse, status_code=status.HTTP_201_CREATED)
async def create_visit_log(visit_data: VisitLogCreate):
    """
    Log an extension agent visit
    """
    try:
        return await visit_log_service.create_visit_log(visit_data)
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


@router_history.get("/{farmer_id}", response_model=List[VisitLogResponse])
async def get_visit_history(
    farmer_id: str = Path(..., example="DC00001", description="The ID of the farmer")
):
    """
    Get visit history for a specific farmer
    """
    logs = await visit_log_service.get_visit_history(farmer_id)
    return logs