"""Input Request Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Path, status
from app.services.input_request_service import input_request_service
from app.schemas.extension.input_request import InputRequestCreate, InputRequestResponse

router = APIRouter()


@router.post("/", response_model=InputRequestResponse, status_code=status.HTTP_201_CREATED)
async def submit_input_request(request_data: InputRequestCreate):
    """
    Submit an input request from an extension agent
    """
    try:
        # In a real app, we would get the agent from context (e.g., JWT token)
        # For now, we just create the request without agent linkage.
        response = await input_request_service.create_input_request(request_data)
        return response
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