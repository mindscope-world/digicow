"""Agent Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from app.services.agent_service import agent_service
from app.schemas.extension.agent import AgentResponse

router = APIRouter()


@router.get("/{agent_id}/dashboard", response_model=dict)
async def get_agent_dashboard(
    agent_id: str = Path(..., examples={"AG001": {"summary": "Example agent ID", "value": "AG001"}}, description="The ID of the agent")
):
    """
    Get dashboard data for a specific agent
    """
    data = await agent_service.get_agent_dashboard(agent_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    return data


@router.get("/{agent_id}/farmers-needing-attention", response_model=List[dict])
async def get_farmers_needing_attention(
    agent_id: str = Path(..., examples={"AG001": {"summary": "Example agent ID", "value": "AG001"}}, description="The ID of the agent")
):
    """
    Get prioritized list of farmers needing attention for a specific agent
    """
    data = await agent_service.get_farmers_needing_attention(agent_id)
    return data