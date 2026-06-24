"""
Main API Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import farmers, training, adoption

api_router = APIRouter()

# Include farmers routes
api_router.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
# Include training routes
api_router.include_router(training.router, prefix="/trainings", tags=["trainings"])
# Include adoption routes
api_router.include_router(adoption.router, prefix="/adoptions", tags=["adoptions"])

# Other routers will be added here as they are implemented
# api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])