"""Agent Service Layer"""
from typing import List, Dict, Any
from app.models.extension.agent import Agent
from app.models.farmer import Farmer
from app.models.extension.visit_log import VisitLog
from app.models.extension.input_request import InputRequest
from datetime import datetime, timedelta


class AgentService:
    """
    Service for Agent-related operations
    """

    @staticmethod
    async def get_agent_dashboard(agent_id: str) -> Dict[str, Any]:
        """
        Get dashboard data for a specific agent
        """
        agent = Agent.get_by_id(agent_id)
        if not agent:
            return {}
        # Count recent visit logs (last 30 days) - visits is RelationshipFrom VisitLog to Agent? Actually we have visits = RelationshipFrom VisitLog to Agent, meaning agent.get_visits() gives VisitLog nodes where the agent is the target? Wait:
        # In Agent: visits = RelationshipFrom("app.models.extension.visit_log.VisitLog", "CONDUCTED")
        # This means: VisitLog --CONDUCTED--> Agent
        # So from Agent, .get_visits() gives the List of VisitLog nodes that have a CONDUCTED relationship TO the agent.
        # That's exactly what we want: visits conducted by this agent.
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_visits = 0
        for visit in agent.get_visits():  # each visit is a VisitLog
            if visit.visit_date >= thirty_days_ago:
                recent_visits += 1
        # Count pending input requests made by this agent
        pending_requests = 0
        for req in agent.get_input_requests():  # input_requests = RelationshipFrom InputRequest to Agent
            if req.status == "pending":
                pending_requests += 1
        # Farmer count in assigned ward (if set)
        farmer_count = 0
        if agent.assigned_ward:
            # We could compute via walking farmers, but skip for now
            farmer_count = 0  # placeholder
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.name,
            "assigned_ward": agent.assigned_ward,
            "is_active": agent.is_active,
            "farmer_count": farmer_count,
            "recent_visits_count": recent_visits,
            "pending_input_requests": pending_requests,
            "last_updated": agent.updated_at
        }

    @staticmethod
    async def get_farmers_needing_attention(agent_id: str) -> List[Dict[str, Any]]:
        """
        Get list of farmers needing attention for a given agent
        Criteria: low engagement score, not contacted recently, etc.
        """
        agent = Agent.get_by_id(agent_id)
        if not agent:
            return []
        # Determine which farmers to consider: if agent has assigned ward, only those farmers; else all farmers
        target_farmers = []
        if agent.assigned_ward:
            # Get farmers located in this ward
            for farmer in Farmer.all():
                ward = farmer.located_in_ward()
                if ward and ward.code == agent.assigned_ward:
                    target_farmers.append(farmer)
        else:
            target_farmers = Farmer.all()
        need_attention = []
        thirty_days_ago = datetime.now() - timedelta(days=30)
        sixty_days_ago = datetime.now() - timedelta(days=60)
        for farmer in target_farmers:
            needs_attention = False
            reasons = []
            if farmer.engagement_score_30d < 30:
                needs_attention = True
                reasons.append("low_engagement_30d")
            if farmer.last_contact:
                if farmer.last_contact < sixty_days_ago:
                    needs_attention = True
                    reasons.append("no_contact_60d")
            else:
                # never contacted
                needs_attention = True
                reasons.append("never_contacted")
            if needs_attention:
                need_attention.append({
                    "farmer_id": farmer.farmer_id,
                    "name": f"Farmer {farmer.farmer_id}",  # placeholder
                    "engagement_score_30d": farmer.engagement_score_30d,
                    "last_contact": farmer.last_contact,
                    "reasons": reasons
                })
        # Sort by engagement score ascending (most needy first)
        need_attention.sort(key=lambda x: x["engagement_score_30d"])
        return need_attention


# Instantiate
agent_service = AgentService()