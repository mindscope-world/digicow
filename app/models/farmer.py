"""Neo4j Farmer Model using Neomodel"""
from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    FloatProperty,
    BooleanProperty,
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom,
    UniqueIdProperty,
)
from datetime import datetime


class Farmer(StructuredNode):
    """
    Farmer Node Model
    """
    # Unique identifier
    farmer_id = StringProperty(unique_index=True, required=True)

    # Demographics
    gender = StringProperty(
        choices=(("Male", "Male"), ("Female", "Female"), ("Other", "Other")),
        required=True
    )
    age_bracket = StringProperty(
        choices=(("18-25", "18-25"), ("26-35", "26-35"), ("36-45", "36-45"), ("46-55", "46-55"), ("56-65", "56-65"), ("65+", "65+")),
        required=True
    )
    phone = StringProperty()

    # Registration & Engagement
    registration_method = StringProperty(
        choices=(("mobile_app", "mobile_app"), ("field_agent", "field_agent"), ("sms", "sms"), ("cooperative_office", "cooperative_office"), ("ussd", "ussd")),
        required=True
    )
    belongs_to_cooperative = BooleanProperty(default=False)

    # Farm Characteristics
    herd_size = IntegerProperty(default=0)
    acres_under_cultivation = FloatProperty(default=0.0)
    primary_enterprise = StringProperty()

    # Timestamps
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty()
    last_contact = DateTimeProperty()

    # Computed scores (updated periodically)
    engagement_score_7d = IntegerProperty(default=0)
    engagement_score_30d = IntegerProperty(default=0)
    engagement_score_90d = IntegerProperty(default=0)
    trend = StringProperty(
        choices=(("up", "up"), ("down", "down"), ("flat", "flat")),
        default="flat"
    )
    status = StringProperty(
        choices=(("Active", "Active"), ("At risk", "At risk"), ("Dormant", "Dormant")),
        default="Active"
    )

    # Relationships
    # Belongs to cooperative
    member_of = RelationshipTo("app.models.cooperative.Cooperative", "MEMBER_OF")

    # Located in ward -> subcounty -> county
    located_in = RelationshipTo("app.models.location.Ward", "LOCATED_IN")

    # Trained by trainers
    trained_by = RelationshipFrom("app.models.trainer.Trainer", "TRAINS")

    # Participated in training sessions
    participated_in = RelationshipTo("app.models.training.TrainingSession", "PARTICIPATED_IN")

    # Has adopted input products (through Adoption model)
    adoptions = RelationshipTo("app.models.adoption.Adoption", "HAS_ADOPTED")

    # Receives advisory recommendations
    receives = RelationshipTo("app.models.advisory.AdvisoryRecommendation", "RECEIVES")

    def __str__(self):
        return f"Farmer({self.farmer_id}: {self.gender}, {self.age_bracket})"

    @property
    def is_active(self):
        return self.status == "Active"

    def update_engagement_scores(self):
        """
        Update engagement scores based on recent activity
        This would be implemented with actual logic in a real system
        """
        # Placeholder implementation
        pass