"""Input Request Model using Direct Neo4j Driver"""
from app.database import get_db
from datetime import datetime
from neo4j.time import DateTime
from app.models.farmer import Farmer
from app.models.input_product.input_product import InputProduct


class InputRequest:
    """InputRequest node model using direct Neo4j driver"""

    LABEL = "InputRequest"

    def __init__(self, farmer_id=None, product_id=None, quantity_requested=None,
                 quantity_approved=0, status="pending", notes=None,
                 date_requested=None, date_fulfilled=None, uid=None):
        self.farmer_id = farmer_id
        self.product_id = product_id
        self.quantity_requested = quantity_requested
        self.quantity_approved = quantity_approved
        self.status = status
        self.notes = notes
        if isinstance(date_requested, (float, int)):
            # Assume it's a Unix timestamp
            self.date_requested = datetime.fromtimestamp(date_requested)
        elif isinstance(date_requested, DateTime):
            # Convert neo4j DateTime to Python datetime
            self.date_requested = date_requested.to_native()
        else:
            self.date_requested = date_requested or datetime.now()
        if isinstance(date_fulfilled, (float, int)):
            self.date_fulfilled = datetime.fromtimestamp(date_fulfilled)
        elif isinstance(date_fulfilled, DateTime):
            self.date_fulfilled = date_fulfilled.to_native()
        else:
            self.date_fulfilled = date_fulfilled
        self.uid = uid or self._generate_uid()

    def _generate_uid(self):
        """Generate a unique ID"""
        import uuid
        return str(uuid.uuid4())

    def save(self):
        """Save input request node to database"""
        db = get_db()
        if not self.uid:
            self.uid = self._generate_uid()

        query = """
        MERGE (ir:InputRequest {uid: $uid})
        ON CREATE SET
            ir.farmer_id = $farmer_id,
            ir.product_id = $product_id,
            ir.quantity_requested = $quantity_requested,
            ir.quantity_approved = $quantity_approved,
            ir.status = $status,
            ir.notes = $notes,
            ir.date_requested = $date_requested
        ON MATCH SET
            ir.farmer_id = $farmer_id,
            ir.product_id = $product_id,
            ir.quantity_requested = $quantity_requested,
            ir.quantity_approved = $quantity_approved,
            ir.status = $status,
            ir.notes = $notes,
            ir.date_requested = $date_requested,
            ir.date_fulfilled = $date_fulfilled
        RETURN ir
        """
        parameters = {
            "uid": self.uid,
            "farmer_id": self.farmer_id,
            "product_id": self.product_id,
            "quantity_requested": self.quantity_requested,
            "quantity_approved": self.quantity_approved,
            "status": self.status,
            "notes": self.notes,
            "date_requested": self.date_requested,
            "date_fulfilled": self.date_fulfilled
        }

        result = db.execute_write(query, parameters)
        return result[0]["ir"] if result else None

    @classmethod
    def get_by_uid(cls, uid):
        """Get input request by UID"""
        db = get_db()
        query = """
        MATCH (ir:InputRequest {uid: $uid})
        RETURN ir
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["ir"]
            return cls(
                farmer_id=record["farmer_id"],
                product_id=record["product_id"],
                quantity_requested=record["quantity_requested"],
                quantity_approved=record["quantity_approved"],
                status=record["status"],
                notes=record.get("notes"),
                date_requested=record["date_requested"],
                date_fulfilled=record.get("date_fulfilled"),
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_id(cls, request_id):
        """Get input request by ID (alias for get_by_uid)"""
        return cls.get_by_uid(request_id)

    @classmethod
    def all(cls):
        """Get all input requests"""
        db = get_db()
        query = """
        MATCH (ir:InputRequest)
        RETURN ir
        """
        result = db.execute_query(query)
        requests = []
        for record in result:
            record_data = record["ir"]
            requests.append(cls(
                farmer_id=record_data["farmer_id"],
                product_id=record_data["product_id"],
                quantity_requested=record_data["quantity_requested"],
                quantity_approved=record_data["quantity_approved"],
                status=record_data["status"],
                notes=record_data.get("notes"),
                date_requested=record_data["date_requested"],
                date_fulfilled=record_data.get("date_fulfilled"),
                uid=record_data["uid"]
            ))
        return requests

    def set_farmer(self, farmer):
        """Set relationship to farmer"""
        db = get_db()
        query = """
        MATCH (ir:InputRequest {uid: $request_uid})
        MATCH (f:Farmer {farmer_id: $farmer_id})
        MERGE (ir)-[:REQUESTED_BY]->(f)
        """
        db.execute_write(query, {
            "request_uid": self.uid,
            "farmer_id": farmer.farmer_id
        })

    def set_input_product(self, product):
        """Set relationship to input product"""
        db = get_db()
        query = """
        MATCH (ir:InputRequest {uid: $request_uid})
        MATCH (ip:InputProduct {uid: $product_uid})
        MERGE (ir)-[:REQUESTS_PRODUCT]->(ip)
        """
        db.execute_write(query, {
            "request_uid": self.uid,
            "product_uid": product.uid
        })

    def set_agent(self, agent):
        """Set relationship to agent (optional)"""
        if agent is None:
            return
        db = get_db()
        query = """
        MATCH (ir:InputRequest {uid: $request_uid})
        MATCH (a:Agent {agent_id: $agent_id})
        MERGE (ir)-[:REQUESTED_BY_AGENT]->(a)
        """
        db.execute_write(query, {
            "request_uid": self.uid,
            "agent_id": agent.agent_id
        })

    def get_farmer(self):
        """Get the farmer associated with this request"""
        db = get_db()
        query = """
        MATCH (ir:InputRequest {uid: $request_uid})-[:REQUESTED_BY]->(f:Farmer)
        RETURN f
        """
        result = db.execute_query(query, {"request_uid": self.uid})
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

    def get_input_product(self):
        """Get the input product associated with this request"""
        db = get_db()
        query = """
        MATCH (ir:InputRequest {uid: $request_uid})-[:REQUESTS_PRODUCT]->(ip:InputProduct)
        RETURN ip
        """
        result = db.execute_query(query, {"request_uid": self.uid})
        if result:
            record = result[0]["ip"]
            return InputProduct(
                name=record["name"],
                type_=record["type"],
                brand=record["brand"],
                cost=record["cost"],
                effectiveness_rating=record["effectiveness_rating"],
                uid=record["uid"]
            )
        return None

    def get_agent(self):
        """Get the agent associated with this request (if any)"""
        from app.models.extension.agent import Agent
        db = get_db()
        query = """
        MATCH (ir:InputRequest {uid: $request_uid})-[:REQUESTED_BY_AGENT]->(a:Agent)
        RETURN a
        """
        result = db.execute_query(query, {"request_uid": self.uid})
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
        return f"Request {self.uid} for {self.quantity_requested} of {self.get_input_product().name if self.get_input_product() else 'N/A'}"