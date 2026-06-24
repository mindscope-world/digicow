"""Input Request Service Layer"""
from typing import Optional
from app.models.extension.input_request import InputRequest
from app.models.farmer import Farmer
from app.models.input_product.input_product import InputProduct
from app.models.extension.agent import Agent
from app.schemas.extension.input_request import InputRequestCreate, InputRequestResponse
from datetime import datetime


class InputRequestService:
    """
    Service class for Input Request operations
    """

    @staticmethod
    async def create_input_request(request_data: InputRequestCreate) -> InputRequestResponse:
        """
        Create a new input request
        """
        # Validate farmer exists
        farmer = Farmer.nodes.get_or_none(farmer_id=request_data.farmer_id)
        if not farmer:
            raise ValueError(f"Farmer with ID {request_data.farmer_id} not found")

        # Validate product exists
        product = InputProduct.nodes.get_or_none(uid=request_data.product_id)
        if not product:
            raise ValueError(f"Input product with ID {request_data.product_id} not found")

        # Create the request
        request_obj = InputRequest(
            status="pending",
            quantity_requested=request_data.quantity_requested,
            notes=request_data.notes,
        )
        request_obj.save()

        # Connect relationships
        request_obj.farmer.connect(farmer)
        request_obj.input_product.connect(product)
        # Agent connection omitted for now (could be system or from context)

        # Prepare response
        return InputRequestResponse(
            id=request_obj.uid,
            farmer_id=request_data.farmer_id,
            product_id=request_data.product_id,
            quantity_requested=request_data.quantity_requested,
            notes=request_data.notes,
            status=request_obj.status,
            quantity_approved=0,
            date_requested=request_obj.date_requested,
            date_fulfilled=None,
        )

    # Additional methods can be added: get_request, update_request, list_requests, etc.

# Instantiate for use in router
input_request_service = InputRequestService()