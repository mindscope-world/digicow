"""
Adoption Service Layer
"""
import uuid
from typing import List, Optional
from datetime import datetime
from app.models.farmer import Farmer
from app.models.input_product import InputProduct
from app.models.adoption import Adoption
from app.schemas.adoption import AdoptionCreate, AdoptionResponse


class AdoptionService:
    """
    Service class for Adoption operations
    """

    @staticmethod
    async def create_adoption(adoption_data: AdoptionCreate) -> AdoptionResponse:
        """
        Record a new adoption event
        """
        # Find the farmer
        farmer = Farmer.nodes.get_or_none(farmer_id=adoption_data.farmer_id)
        if not farmer:
            raise ValueError(f"Farmer with ID {adoption_data.farmer_id} not found")

        # Find the input product by name
        input_product = InputProduct.nodes.get_or_none(name=adoption_data.input_product_name)
        if not input_product:
            raise ValueError(f"Input product with name '{adoption_data.input_product_name}' not found")

        # Create the adoption event
        adoption = Adoption(
            uid=str(uuid.uuid4()),
            date_adopted=datetime.now()
        )
        adoption.save()

        # Connect the adoption to the farmer and input product
        adoption.farmer.connect(farmer)
        adoption.input_product.connect(input_product)

        # Return the adoption response
        return AdoptionResponse(
            id=adoption.uid,
            farmer_id=adoption.farmer.farmer_id,
            input_product_name=adoption.input_product.name,
            date_adopted=adoption.date_adopted
        )

    @staticmethod
    async def get_farmer_adoption_history(farmer_id: str) -> List[AdoptionResponse]:
        """
        Get adoption timeline for a farmer
        """
        # Find the farmer
        farmer = Farmer.nodes.get_or_none(farmer_id=farmer_id)
        if not farmer:
            return []  # Return empty list if farmer not found

        # Get all adoptions for this farmer
        adoptions = farmer.adoptions.all()  # This is the relationship from Farmer to Adoption

        # Convert to response models
        results = []
        for adoption in adoptions:
            results.append(AdoptionResponse(
                id=adoption.uid,
                farmer_id=adoption.farmer.farmer_id,
                input_product_name=adoption.input_product.name,
                date_adopted=adoption.date_adopted
            ))
        # Sort by date_adopted descending (most recent first)
        results.sort(key=lambda x: x.date_adopted, reverse=True)
        return results