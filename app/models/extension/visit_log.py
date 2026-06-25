"""Visit Log Model"""
from neomodel import StructuredNode, StringProperty, UniqueIdProperty, DateTimeProperty, RelationshipTo
from ..farmer import Farmer
from .agent import Agent


class VisitLog(StructuredNode):
    """
    Visit Log Node Model
    """
    uid = UniqueIdProperty()
    visit_date = DateTimeProperty(default_now=True)
    purpose = StringProperty()  # e.g., training, input delivery, follow-up
    notes = StringProperty()  # free-form notes

    # Relationships
    farmer = RelationshipTo(Farmer, "VISITED")
    agent = RelationshipTo(Agent, "CONDUCTED")

    def __str__(self):
        return f"Visit {self.uid} on {self.visit_date}"