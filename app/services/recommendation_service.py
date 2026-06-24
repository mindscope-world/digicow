"""
Recommendation Service Layer
"""
import random
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.farmer import Farmer
from app.models.advisory import AdvisoryRecommendation
from app.models.location.ward import Ward
from app.schemas.recommendation import (
    AdvisoryRecommendationResponse,
    TrendingTopic,
    RecommendationGenerateResponse,
)


class RecommendationService:
    """
    Service for generating and retrieving advisory recommendations.
    """

    @staticmethod
    async def get_farmer_recommendations(farmer_id: Farmer) -> List[AdvisoryRecommendationResponse]:
        """
        Get personalized recommendations for a specific farmer.
        """
        # In a real implementation, we would query the graph for recommendations
        # linked to this farmer via RECEIVES relationship.
        # For now, we return some dummy data or existing recommendations.
        recommendations = []
        try:
            # Assuming AdvisoryRecommendation has a relationship 'received_by' from Farmer
            # We need to get recommendations where this farmer is the receiver.
            # The relationship defined in AdvisoryRecommendation is:
            # received_by = RelationshipFrom(Farmer, "RECEIVES")
            # So to get recommendations for a farmer, we need to traverse the reverse.
            # neomodel does not provide automatic reverse traversal unless we define a RelationshipTo.
            # We'll instead query all recommendations and filter by checking if farmer in rec.received_by.
            # For simplicity, we'll return a static list.
            pass
        except Exception:
            pass

        # Dummy data for demonstration
        dummy_recs = [
            {
                "id": f"rec_{farmer.farmer_id}_{i}",
                "recommendation_type": ["spraying", "planting", "harvesting", "feeding"][i % 4],
                "advice": f"Recommendation {i+1} for farmer {farmer.farmer_id}: Apply best practice X.",
                "date_given": datetime.utcnow() - timedelta(days=i),
                "priority": ["low", "medium", "high"][i % 3],
                "farmer_id": farmer.farmer_id,
            }
            for i in range(3)
        ]
        return [AdvisoryRecommendationResponse(**rec) for rec in dummy_recs]

    @staticmethod
    async def get_ward_recommendations(ward_id: str) -> List[AdvisoryRecommendationResponse]:
        """
        Get ward-level recommendations (aggregated for farmers in a ward).
        """
        # Dummy implementation
        dummy_recs = [
            {
                "id": f"ward_{ward_id}_rec_{i}",
                "recommendation_type": ["irrigation", "soil_test", "variety_selection"][i % 3],
                "advice": f"Ward {ward_id} recommendation {i+1}: Consider action Y.",
                "date_given": datetime.utcnow() - timedelta(days=i*2),
                "priority": ["medium", "high"][i % 2],
                "farmer_id": None,  # ward-level not tied to specific farmer
            }
            for i in range(3)
        ]
        return [AdvisoryRecommendationResponse(**rec) for rec in dummy_recs]

    @staticmethod
    async def generate_recommendations() -> RecommendationGenerateResponse:
        """
        Trigger recommendation generation (e.g., run ML model or batch job).
        """
        # Placeholder: In reality, this would trigger a background job.
        # We'll just simulate generating some recommendations.
        count = random.randint(10, 50)
        return RecommendationGenerateResponse(
            message=f"Generated {count} new recommendations.",
            count=count,
        )

    @staticmethod
    async def get_trending_topics(region: Optional[str] = None) -> List[TrendingTopic]:
        """
        Get trending training topics by region (or globally if region not specified).
        """
        # Dummy data
        topics = [
            ("Disease prevention", 22),
            ("Improved breeding", 18),
            ("Feed optimization", 15),
            ("Milk quality testing", 12),
            ("Record keeping", 10),
        ]
        result = []
        for topic, freq in topics:
            result.append(
                TrendingTopic(
                    topic=topic,
                    frequency=freq,
                    region=region,
                )
            )
        # Sort by frequency descending
        result.sort(key=lambda x: x.frequency, reverse=True)
        return result


# Convenience instances
recommendation_service = RecommendationService()