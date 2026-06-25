"""Extension Agent Model"""
from neomodel import StructuredNode, StringProperty, UniqueIdProperty, DateTimeProperty, BooleanProperty, RelationshipTo, RelationshipFrom
from ..farmer import Farmer
from datetime import datetime


class Agent(StructuredNode):
    """
    Extension Agent Node Model
    """
    # Unique identifier
    agent_id = StringProperty(unique_index=True, required=True)

    # Basic info
    name = StringProperty(required=True)
    phone = StringProperty()
    email = StringProperty()

    # Assignment
    assigned_ward = StringProperty()  # Could link to Ward node, but keep simple for now
    is_active = BooleanProperty(default=True)

    # Timestamps
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty()

    # Relationships
    # Agent can visit many farmers (VisitLog) - incoming from VisitLog
    visits = RelationshipFrom("app.models.extension.visit_log.VisitLog", "CONDUCTED")
    # Agent can request inputs on behalf of farmers - incoming from InputRequest
    input_requests = RelationshipFrom("app.models.extension.input_request.InputRequest", "REQUESTED_BY_AGENT")

    def __str__(self):
        return f"{self.name} ({self.agent_id})"