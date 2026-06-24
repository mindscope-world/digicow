"""Input Product Model"""
from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipFrom
from ..farmer import Farmer


class InputProduct(StructuredNode):
    name = StringProperty(required=True)
    category = StringProperty()  # e.g., seed, fertilizer, pesticide
    price = StringProperty()  # could be FloatProperty but keep as string for simplicity

    # Relationships
    # Note: The relationship to Adoption is defined in the Adoption model as:
    #   input_product = RelationshipFrom(InputProduct, "IS_ADOPTED_BY")
    # So from InputProduct, we can get adoptions via the reverse of that relationship.
    adoptions = RelationshipFrom("app.models.adoption.Adoption", "IS_ADOPTED_BY")

    def __str__(self):
        return self.name