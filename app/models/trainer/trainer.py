"""Trainer Model"""
from neomodel import StructuredNode, StringProperty, RelationshipTo
from ..farmer import Farmer

class Trainer(StructuredNode):
    name = StringProperty(required=True)
    specialization = StringProperty()  # e.g., agronomy, livestock, agribusiness
    employee_id = StringProperty(unique_index=True)

    # Relationships
    trains = RelationshipTo(Farmer, "TRAINS")

    def __str__(self):
        return self.name