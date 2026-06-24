"""
Input Product Endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from app.services.input_product_service import input_product_service
from app.schemas.input_product import InputProductResponse

router = APIRouter()


@router.get("/", response_model=List[InputProductResponse])
async def list_input_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
):
    """
    List input products with pagination.
    """
    products = await input_product_service.get_input_products(skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=InputProductResponse)
async def get_input_product(
    product_id: str = Path(..., example="IP001", description="The ID of the input product")
):
    """
    Get details of a specific input product by ID.
    """
    product = await input_product_service.get_input_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Input product with ID {product_id} not found",
        )
    return product