"""Extension Agent Model using Direct Neo4j Driver"""
from app.database import get_db
from datetime import datetime
from neo4j.time import DateTime
from app.models.farmer import Farmer


class Agent:
    """Agent node model using direct Neo4j driver"""

    LABEL = "Agent"

    def __init__(self, agent_id=None, name=None, phone=None, email=None,
                 assigned_ward=None, is_active=True, uid=None,
                 created_at=None, updated_at=None):
        self.agent_id = agent_id
        self.name = name
        self.phone = phone
        self.email = email
        self.assigned_ward = assigned_ward
        self.is_active = is_active
        if isinstance(created_at, (float, int)):
            # Assume it's a Unix timestamp
            self.created_at = datetime.fromtimestamp(created_at)
        elif isinstance(created_at, DateTime):
            # Convert neo4j DateTime to Python datetime
            self.created_at = created_at.to_native()
        else:
            self.created_at = created_at or datetime.now()
        if isinstance(updated_at, (float, int)):
            self.updated_at = datetime.fromtimestamp(updated_at)
        elif isinstance(updated_at, DateTime):
            self.updated_at = updated_at.to_native()
        else:
            self.updated_at = updated_at
        self.uid = uid

    def save(self):
        """Save agent node to database"""
        db = get_db()
        if not self.uid:
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (a:Agent {agent_id: $agent_id})
        ON CREATE SET
            a.uid = $uid,
            a.name = $name,
            a.phone = $phone,
            a.email = $email,
            a.assigned_ward = $assigned_ward,
            a.is_active = $is_active,
            a.created_at = $created_at
        ON MATCH SET
            a.name = $name,
            a.phone = $phone,
            a.email = $email,
            a.assigned_ward = $assigned_ward,
            a.is_active = $is_active,
            a.updated_at = $updated_at
        RETURN a
        """
        parameters = {
            "agent_id": self.agent_id,
            "uid": self.uid,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "assigned_ward": self.assigned_ward,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        result = db.execute_write(query, parameters)
        return result[0]["a"] if result else None

    @classmethod
    def get_by_id(cls, agent_id):
        """Get agent by agent_id"""
        db = get_db()
        query = """
        MATCH (a:Agent {agent_id: $agent_id})
        RETURN a
        """
        result = db.execute_query(query, {"agent_id": agent_id})
        if result:
            record = result[0]["a"]
            return cls(
                agent_id=record["agent_id"],
                name=record["name"],
                phone=record.get("phone"),
                email=record.get("email"),
                assigned_ward=record.get("assigned_ward"),
                is_active=record.get("is_active", True),
                uid=record.get("uid"),
                created_at=record.get("created_at"),
                updated_at=record.get("updated_at")
            )
        return None

    @classmethod
    def get_by_uid(cls, uid):
        """Get agent by UID"""
        db = get_db()
        query = """
        MATCH (a:Agent {uid: $uid})
        RETURN a
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["a"]
            return cls(
                agent_id=record["agent_id"],
                name=record["name"],
                phone=record.get("phone"),
                email=record.get("email"),
                assigned_ward=record.get("assigned_ward"),
                is_active=record.get("is_active", True),
                uid=record["uid"],
                created_at=record.get("created_at"),
                updated_at=record.get("updated_at")
            )
        return None

    @classmethod
    def all(cls):
        """Get all agents"""
        db = get_db()
        query = """
        MATCH (a:Agent)
        RETURN a
        """
        result = db.execute_query(query)
        agents = []
        for record in result:
            record_data = record["a"]
            agents.append(cls(
                agent_id=record_data["agent_id"],
                name=record_data["name"],
                phone=record_data.get("phone"),
                email=record_data.get("email"),
                assigned_ward=record_data.get("assigned_ward"),
                is_active=record_data.get("is_active", True),
                uid=record_data.get("uid"),
                created_at=record_data.get("created_at"),
                updated_at=record_data.get("updated_at")
            ))
        return agents

    def get_visits(self):
        """Get visits (VisitLog nodes) conducted by this agent"""
        from app.models.extension.visit_log import VisitLog
        db = get_db()
        query = """
        MATCH (a:Agent {agent_id: $agent_id})<-[:CONDUCTED]-(vl:VisitLog)
        RETURN vl
        """
        result = db.execute_query(query, {"agent_id": self.agent_id})
        visits = []
        for record in result:
            record_data = record["vl"]
            visits.append(VisitLog(
                purpose=record_data["purpose"],
                notes=record_data["notes"],
                visit_date=record_data["visit_date"],
                uid=record_data["uid"]
            ))
        return visits

    def get_input_requests(self):
        """Get input requests made by this agent"""
        from app.models.extension.input_request import InputRequest
        db = get_db()
        query = """
        MATCH (a:Agent {agent_id: $agent_id})<-[:REQUESTED_BY_AGENT]-(ir:InputRequest)
        RETURN ir
        """
        result = db.execute_query(query, {"agent_id": self.agent_id})
        requests = []
        for record in result:
            record_data = record["ir"]
            requests.append(InputRequest(
                farmer_id=record_data["farmer_id"],
                product_id=record_data["product_id"],
                quantity=record_data["quantity"],
                status=record_data["status"],
                uid=record_data["uid"]
            ))
        return requests

    def __str__(self):
        return f"{self.name} ({self.agent_id})"