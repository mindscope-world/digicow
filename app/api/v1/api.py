"""
Main API Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import farmers, training, adoption, recommendations, input, input_request, analytics, agent, visit_log, demand_forecast

api_router = APIRouter()

# Include farmers routes
api_router.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
# Include training routes
api_router.include_router(training.router, prefix="/trainings", tags=["trainings"])
# Include adoption routes
api_router.include_router(adoption.router, prefix="/adoptions", tags=["adoptions"])
# Include recommendations routes
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
# Include input product routes
api_router.include_router(input.router, prefix="/inputs", tags=["inputs"])
# Include input request routes
api_router.include_router(input_request.router, prefix="/input-requests", tags=["input-requests"])
# Include analytics routes
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
# Include agent routes
api_router.include_router(agent.router, prefix="/agents", tags=["agents"])
# Include visit log routes
api_router.include_router(visit_log.router_log)  # already has "/visit-logs" prefix
api_router.include_router(visit_log.router_history)  # already has "/visit-history" prefix
# Include demand forecast routes
api_router.include_router(demand_forecast.router, prefix="/demand-forecast", tags=["demand-forecast"])

# Other routers will be added here as they are implemented