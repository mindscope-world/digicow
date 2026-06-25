"""
Subcounty Model using Direct Neo4j Driver
"""
from app.database import get_db

class Subcounty:
    """Subcounty node model using direct Neo4j driver"""

    LABEL = "Subcounty"

    def __init__(self, name=None, code=None, uid=None):
        self.name = name
        self.code = code or (name[:3].upper() if name else None)
        self.uid = uid

    def save(self):
        """Save subcounty node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (s:Subcounty {code: $code})
        ON CREATE SET
            s.uid = $uid,
            s.name = $name
        ON MATCH SET
            s.name = $name
        RETURN s
        """
        parameters = {
            "name": self.name,
            "code": self.code,
            "uid": self.uid
        }

        result = db.execute_write(query, parameters)
        return result[0]["s"] if result else None

    @classmethod
    def get_by_code(cls, code):
        """Get subcounty by code"""
        db = get_db()
        query = """
        MATCH (s:Subcounty {code: $code})
        RETURN s
        """
        result = db.execute_query(query, {"code": code})
        if result:
            record = result[0]["s"]
            return cls(
                name=record["name"],
                code=record["code"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_uid(cls, uid):
        """Get subcounty by UID"""
        db = get_db()
        query = """
        MATCH (s:Subcounty {uid: $uid})
        RETURN s
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["s"]
            return cls(
                name=record["name"],
                code=record["code"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all subcounties"""
        db = get_db()
        query = """
        MATCH (s:Subcounty)
        RETURN s
        """
        result = db.execute_query(query)
        subcounties = []
        for record in result:
            record_data = record["s"]
            subcounties.append(cls(
                name=record_data["name"],
                code=record_data["code"],
                uid=record_data["uid"]
            ))
        return subcounties

    def county(self):
        """Get relationship to county (container)"""
        db = get_db()
        query = """
        MATCH (s:Subcounty {code: $code})<-[:CONTAINS]-(c:County)
        RETURN c
        """
        result = db.execute_query(query, {"code": self.code})
        from app.models.location.county import County
        counties = []
        for record in result:
            record_data = record["c"]
            counties.append(County(
                name=record_data["name"],
                code=record_data["code"],
                uid=record_data["uid"]
            ))
        return counties

    def wards(self):
        """Get relationship to wards (contained)"""
        db = get_db()
        query = """
        MATCH (s:Subcounty {code: $code})-[:CONTAINS]->(w:Ward)
        RETURN w
        """
        result = db.execute_query(query, {"code": self.code})
        from app.models.location.ward import Ward
        wards = []
        for record in result:
            record_data = record["w"]
            wards.append(Ward(
                name=record_data["name"],
                code=record_data["code"],
                uid=record_data["uid"]
            ))
        return wards