"""
Cooperative Model using Direct Neo4j Driver
"""
from app.database import get_db

class Cooperative:
    """Cooperative node model using direct Neo4j driver"""

    LABEL = "Cooperative"

    def __init__(self, name=None, location_details=None, uid=None):
        self.name = name
        self.location_details = location_details
        self.uid = uid

    def save(self):
        """Save cooperative node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (c:Cooperative {name: $name})
        ON CREATE SET
            c.uid = $uid,
            c.location_details = $location_details
        ON MATCH SET
            c.location_details = $location_details
        RETURN c
        """
        parameters = {
            "name": self.name,
            "uid": self.uid,
            "location_details": self.location_details
        }

        result = db.execute_write(query, parameters)
        return result[0]["c"] if result else None

    @classmethod
    def get_by_name(cls, name):
        """Get cooperative by name"""
        db = get_db()
        query = """
        MATCH (c:Cooperative {name: $name})
        RETURN c
        """
        result = db.execute_query(query, {"name": name})
        if result:
            record = result[0]["c"]
            return cls(
                name=record["name"],
                location_details=record["location_details"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_uid(cls, uid):
        """Get cooperative by UID"""
        db = get_db()
        query = """
        MATCH (c:Cooperative {uid: $uid})
        RETURN c
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["c"]
            return cls(
                name=record["name"],
                location_details=record["location_details"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all cooperatives"""
        db = get_db()
        query = """
        MATCH (c:Cooperative)
        RETURN c
        """
        result = db.execute_query(query)
        cooperatives = []
        for record in result:
            record_data = record["c"]
            cooperatives.append(cls(
                name=record_data["name"],
                location_details=record_data["location_details"],
                uid=record_data["uid"]
            ))
        return cooperatives

    def members(self):
        """Get relationship to farmers (members)"""
        db = get_db()
        query = """
        MATCH (c:Cooperative {name: $name})<-[:MEMBER_OF]-(f:Farmer)
        RETURN f
        """
        result = db.execute_query(query, {"name": self.name})
        from app.models.farmer import Farmer
        members = []
        for record in result:
            record_data = record["f"]
            members.append(Farmer(
                farmer_id=record_data["farmer_id"],
                gender=record_data["gender"],
                age_bracket=record_data["age_bracket"],
                registration_method=record_data["registration_method"],
                belongs_to_cooperative=record_data["belongs_to_cooperative"],
                phone=record_data["phone"],
                herd_size=record_data["herd_size"],
                acres_under_cultivation=record_data["acres_under_cultivation"],
                primary_enterprise=record_data["primary_enterprise"],
                uid=record_data["uid"]
            ))
        return members