"""Adoption Model"""
from neomodel import StructuredNode, DateTimeProperty, StringProperty, RelationshipTo, RelationshipFrom
from .farmer import Farmer
from .input_product.input_product import InputProduct


class Adoption(StructuredNode):
    """
    Adoption event model to track when farmers adopt input products
    """
    uid = StringProperty(unique_index=True, required=True)  # Unique identifier for the adoption event
    date_adopted = DateTimeProperty(default_now=True)

    # Relationships
    farmer = RelationshipTo(Farmer, "HAS_ADOPTED")
    input_product = RelationshipFrom(InputProduct, "IS_ADOPTED_BY")

    def __str__(self):
        return f"{self.input_product.name} adopted by {self.farmer.farmer_id} on {self.date_adopted}"