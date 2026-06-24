"""
Input Product Service Layer
"""
from typing import List, Optional
from app.models.input_product.input_product import InputProduct
from app.schemas.input_product import InputProductResponse


class InputProductService:
    """
    Service class for Input Product operations
    """

    @staticmethod
    async def get_input_products(
        skip: int = 0,
        limit: int = 100,
    ) -> List[InputProductResponse]:
        """
        Get list of input products with pagination
        """
        products = InputProduct.nodes.skip(skip).limit(limit)
        return [InputProductResponse.model_validate(product) for product in products]

    @staticmethod
    async def get_input_product(product_id: str) -> Optional[InputProductResponse]:
        """
        Get a single input product by ID
        """
        # Note: In the InputProduct model, the unique identifier is 'uid' (from UniqueIdProperty)
        product = InputProduct.nodes.get_or_none(uid=product_id)
        if not product:
            return None
        return InputProductResponse.model_validate(product)

    # We can add create, update, delete if needed, but not requested

# Instantiate for use in the router
input_product_service = InputProductService()