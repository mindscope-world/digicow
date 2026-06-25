"""
County Model using Direct Neo4j Driver
"""
from app.database import get_db

class County:
    """County node model using direct Neo4j driver"""

    LABEL = "County"

    def __init__(self, name=None, code=None, uid=None):
        self.name = name
        self.code = code or (name[:3].upper() if name else None)
        self.uid = uid

    def save(self):
        """Save county node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (c:County {code: $code})
        ON CREATE SET
            c.uid = $uid,
            c.name = $name
        ON MATCH SET
            c.name = $name
        RETURN c
        """
        parameters = {
            "name": self.name,
            "code": self.code,
            "uid": self.uid
        }

        result = db.execute_write(query, parameters)
        return result[0]["c"] if result else None

    @classmethod
    def get_by_code(cls, code):
        """Get county by code"""
        db = get_db()
        query = """
        MATCH (c:County {code: $code})
        RETURN c
        """
        result = db.execute_query(query, {"code": code})
        if result:
            record = result[0]["c"]
            return cls(
                name=record["name"],
                code=record["code"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_uid(cls, uid):
        """Get county by UID"""
        db = get_db()
        query = """
        MATCH (c:County {uid: $uid})
        RETURN c
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["c"]
            return cls(
                name=record["name"],
                code=record["code"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all counties"""
        db = get_db()
        query = """
        MATCH (c:County)
        RETURN c
        """
        result = db.execute_query(query)
        counties = []
        for record in result:
            record_data = record["c"]
            counties.append(cls(
                name=record_data["name"],
                code=record_data["code"],
                uid=record_data["uid"]
            ))
        return counties

    def subcounties(self):
        """Get relationship to subcounties (contained)"""
        db = get_db()
        query = """
        MATCH (c:County {code: $code})-[:CONTAINS]->(s:Subcounty)
        RETURN s
        """
        result = db.execute_query(query, {"code": self.code})
        from app.models.location.subcounty import Subcounty
        subcounties = []
        for record in result:
            record_data = record["s"]
            subcounties.append(Subcounty(
                name=record_data["name"],
                code=record_data["code"],
                uid=record_data["uid"]
            ))
        return subcounties