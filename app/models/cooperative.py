"""Cooperative Model"""
from neomodel import StructuredNode, StringProperty, RelationshipFrom
from .farmer import Farmer

class Cooperative(StructuredNode):
    name = StringProperty(required=True)
    location_details = StringProperty()
    
    # Relationships
    members = RelationshipFrom(Farmer, "MEMBER_OF")
    
    def __str__(self):
        return self.name
