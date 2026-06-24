"""Advisory Recommendation Model"""
from neomodel import StructuredNode, StringProperty, DateTimeProperty, UniqueIdProperty, RelationshipFrom
from ..farmer import Farmer

class AdvisoryRecommendation(StructuredNode):
    recommendation_type = StringProperty()  # e.g., spraying, planting, harvesting
    advice = StringProperty()
    date_given = DateTimeProperty(default_now=True)
    priority = StringProperty()  # low, medium, high

    # Relationships
    received_by = RelationshipFrom(Farmer, "RECEIVES")

    def __str__(self):
        return f"{self.recommendation_type}: {self.advice[:50]}"