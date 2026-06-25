"""Demand Forecast Service Layer"""
from typing import List
from app.models.location.ward import Ward
from app.schemas.demand_forecast import DemandForecastResponse, DemandForecastItem
from datetime import datetime


class DemandForecastService:
    """
    Service for demand forecasting (placeholder implementation)
    """

    @staticmethod
    async def get_demand_forecast(ward_id: str) -> List[DemandForecastItem]:
        """
        Get demand forecast for input products in a given ward
        Returns a list of forecast items (placeholder data)
        """
        # Validate ward exists (optional)
        ward = Ward.get_by_code(ward_id)
        # If ward not found, we still return dummy data for demonstration
        # In a real implementation, we would compute based on historical adoption
        # For now, return static example data
        dummy_forecast = [
            DemandForecastItem(
                product_id="prod_ maize_seed_001",
                product_name="Improved Maize Seed",
                predicted_demand=150.0,
                confidence=0.88,
                time_period="2024-02"
            ),
            DemandForecastItem(
                product_id="prod_fert_002",
                product_name="NPK Fertilizer 20-10-10",
                predicted_demand=200.0,
                confidence=0.75,
                time_period="2024-02"
            ),
            DemandForecastItem(
                product_id="prod_pest_003",
                product_name="Organic Pesticide",
                predicted_demand=50.0,
                confidence=0.9,
                time_period="2024-02"
            )
        ]
        return dummy_forecast


# Instantiate
demand_forecast_service = DemandForecastService()