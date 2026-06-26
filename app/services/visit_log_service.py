"""Visit Log Service Layer"""
from typing import List, Optional
from app.models.extension.visit_log import VisitLog
from app.models.farmer import Farmer
from app.models.extension.agent import Agent
from app.schemas.extension.visit_log import VisitLogCreate, VisitLogResponse
from datetime import datetime


class VisitLogService:
    """
    Service for Visit Log operations
    """

    @staticmethod
    async def create_visit_log(visit_data: VisitLogCreate) -> VisitLogResponse:
        """
        Create a new visit log entry
        """
        # Validate farmer exists
        farmer = Farmer.get_by_id(visit_data.farmer_id)
        if not farmer:
            raise ValueError(f"Farmer with ID {visit_data.farmer_id} not found")
        # Validate agent exists if agent_id provided
        agent = None
        if visit_data.agent_id:
            agent = Agent.get_by_id(visit_data.agent_id)
            if not agent:
                raise ValueError(f"Agent with ID {visit_data.agent_id} not found")
        # Create visit log
        visit_log = VisitLog(
            purpose=visit_data.purpose,
            notes=visit_data.notes
        )
        visit_log.save()
        # Connect relationships
        visit_log.connect_farmer(farmer)
        if agent:
            visit_log.connect_agent(agent)
        # Return response
        return VisitLogResponse(
            id=visit_log.uid,
            farmer_id=visit_data.farmer_id,
            purpose=visit_data.purpose,
            notes=visit_data.notes,
            agent_id=visit_data.agent_id,
            visit_date=visit_log.visit_date
        )

    @staticmethod
    async def get_visit_history(farmer_id: str) -> List[VisitLogResponse]:
        """
        Get visit history for a specific farmer
        """
        farmer = Farmer.get_by_id(farmer_id)
        if not farmer:
            return []
        # Find all VisitLog nodes where the farmer relationship matches
        visit_logs = []
        for vl in VisitLog.all():
            # Check if this visit log is for the given farmer
            f = vl.farmer()  # returns Farmer object or None
            if f and f.farmer_id == farmer_id:
                visit_logs.append(vl)
        # Sort by date descending
        visit_logs.sort(key=lambda x: x.visit_date, reverse=True)
        result = []
        for vl in visit_logs:
            agent_obj = vl.agent()
            agent_id = agent_obj.agent_id if agent_obj else None
            result.append(VisitLogResponse(
                id=vl.uid,
                farmer_id=farmer_id,
                purpose=vl.purpose,
                notes=vl.notes,
                agent_id=agent_id,
                visit_date=vl.visit_date
            ))
        return result


# Instantiate
visit_log_service = VisitLogService()