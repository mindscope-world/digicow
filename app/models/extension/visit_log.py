"""Visit Log Model using Direct Neo4j Driver"""
from app.database import get_db
from datetime import datetime
from app.models.farmer import Farmer
from neo4j.time import DateTime


class VisitLog:
    """VisitLog node model using direct Neo4j driver"""

    LABEL = "VisitLog"

    def __init__(self, purpose=None, notes=None, visit_date=None, uid=None):
        self.purpose = purpose
        self.notes = notes
        if isinstance(visit_date, (float, int)):
            # Assume it's a Unix timestamp
            self.visit_date = datetime.fromtimestamp(visit_date)
        elif isinstance(visit_date, DateTime):
            # Convert neo4j DateTime to Python datetime
            self.visit_date = visit_date.to_native()
        else:
            self.visit_date = visit_date or datetime.now()
        self.uid = uid or self._generate_uid()

    def _generate_uid(self):
        """Generate a unique ID"""
        import uuid
        return str(uuid.uuid4())

    def save(self):
        """Save visit log node to database"""
        db = get_db()
        if not self.uid:
            self.uid = self._generate_uid()

        query = """
        MERGE (vl:VisitLog {uid: $uid})
        ON CREATE SET
            vl.purpose = $purpose,
            vl.notes = $notes,
            vl.visit_date = $visit_date
        ON MATCH SET
            vl.purpose = $purpose,
            vl.notes = $notes,
            vl.visit_date = $visit_date
        RETURN vl
        """
        parameters = {
            "uid": self.uid,
            "purpose": self.purpose,
            "notes": self.notes,
            "visit_date": self.visit_date
        }

        result = db.execute_write(query, parameters)
        return result[0]["vl"] if result else None

    @classmethod
    def get_by_uid(cls, uid):
        """Get visit log by UID"""
        db = get_db()
        query = """
        MATCH (vl:VisitLog {uid: $uid})
        RETURN vl
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["vl"]
            return cls(
                purpose=record["purpose"],
                notes=record.get("notes"),
                visit_date=record["visit_date"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_id(cls, visit_id):
        """Get visit log by ID (alias for get_by_uid)"""
        return cls.get_by_uid(visit_id)

    @classmethod
    def all(cls):
        """Get all visit logs"""
        db = get_db()
        query = """
        MATCH (vl:VisitLog)
        RETURN vl
        """
        result = db.execute_query(query)
        visits = []
        for record in result:
            record_data = record["vl"]
            visits.append(cls(
                purpose=record_data["purpose"],
                notes=record_data.get("notes"),
                visit_date=record_data["visit_date"],
                uid=record_data["uid"]
            ))
        return visits

    def connect_farmer(self, farmer):
        """Create relationship to farmer"""
        db = get_db()
        query = """
        MATCH (vl:VisitLog {uid: $visit_log_uid})
        MATCH (f:Farmer {farmer_id: $farmer_id})
        MERGE (vl)-[:VISITED]->(f)
        """
        db.execute_write(query, {
            "visit_log_uid": self.uid,
            "farmer_id": farmer.farmer_id
        })

    def connect_agent(self, agent):
        """Create relationship to agent"""
        db = get_db()
        query = """
        MATCH (vl:VisitLog {uid: $visit_log_uid})
        MATCH (a:Agent {agent_id: $agent_id})
        MERGE (vl)-[:CONDUCTED]->(a)
        """
        db.execute_write(query, {
            "visit_log_uid": self.uid,
            "agent_id": agent.agent_id
        })

    def farmer(self):
        """Get the farmer associated with this visit log"""
        db = get_db()
        query = """
        MATCH (vl:VisitLog {uid: $visit_log_uid})-[:VISITED]->(f:Farmer)
        RETURN f
        """
        result = db.execute_query(query, {"visit_log_uid": self.uid})
        if result:
            record = result[0]["f"]
            return Farmer(
                farmer_id=record["farmer_id"],
                gender=record["gender"],
                age_bracket=record["age_bracket"],
                registration_method=record["registration_method"],
                belongs_to_cooperative=record["belongs_to_cooperative"],
                phone=record["phone"],
                herd_size=record["herd_size"],
                acres_under_cultivation=record["acres_under_cultivation"],
                primary_enterprise=record["primary_enterprise"],
                uid=record["uid"],
                created_at=record.get("created_at"),
                updated_at=record.get("updated_at"),
                last_contact=record.get("last_contact"),
                engagement_score_7d=record.get("engagement_score_7d", 0),
                engagement_score_30d=record.get("engagement_score_30d", 0),
                engagement_score_90d=record.get("engagement_score_90d", 0),
                trend=record.get("trend", "flat"),
                status=record.get("status", "Active")
            )
        return None

    def agent(self):
        """Get the agent associated with this visit log"""
        from app.models.extension.agent import Agent
        db = get_db()
        query = """
        MATCH (vl:VisitLog {uid: $visit_log_uid})-[:CONDUCTED]->(a:Agent)
        RETURN a
        """
        result = db.execute_query(query, {"visit_log_uid": self.uid})
        if result:
            record = result[0]["a"]
            return Agent(
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

    def __str__(self):
        return f"Visit {self.uid} on {self.visit_date}"