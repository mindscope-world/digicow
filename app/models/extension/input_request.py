"""Input Request Model"""
from neomodel import StructuredNode, StringProperty, UniqueIdProperty, DateTimeProperty, IntegerProperty, RelationshipTo
from ..farmer import Farmer
from ..input_product.input_product import InputProduct
from ..extension.agent import Agent  # optional


class InputRequest(StructuredNode):
    """
    Input Request Node Model
    """
    uid = UniqueIdProperty()
    status = StringProperty(default="pending")  # pending, approved, rejected, fulfilled
    quantity_requested = IntegerProperty()
    quantity_approved = IntegerProperty(default=0)
    notes = StringProperty()
    date_requested = DateTimeProperty(default_now=True)
    date_fulfilled = DateTimeProperty()

    # Relationships
    farmer = RelationshipTo(Farmer, "REQUESTED_BY")
    input_product = RelationshipTo(InputProduct, "REQUESTS_PRODUCT")
    # Optional: agent who submitted the request
    agent = RelationshipTo(Agent, "REQUESTED_BY_AGENT", cardinality='zero_or_one')  # optional

    def __str__(self):
        return f"Request {self.uid} for {self.quantity_requested} of {self.input_product.name if self.input_product else 'N/A'}"