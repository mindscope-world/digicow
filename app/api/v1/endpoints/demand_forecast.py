"""Demand Forecast Endpoint"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, Path, status
from app.services.demand_forecast_service import demand_forecast_service
from app.schemas.demand_forecast import DemandForecastResponse, DemandForecastItem

router = APIRouter()


@router.get("/{ward}", response_model=DemandForecastResponse)
async def get_demand_forecast(
    ward: str = Path(..., example="W001", description="The ward code")
):
    """
    Get input demand forecast for a specific ward
    """
    try:
        forecast_list = await demand_forecast_service.get_demand_forecast(ward)
        return DemandForecastResponse(
            ward_id=ward,
            forecast=forecast_list,
            generated_at=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to generate demand forecast: {str(e)}"
        )