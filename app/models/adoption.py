"""
Adoption Model using Direct Neo4j Driver
"""
from app.database import get_db
from datetime import datetime

class Adoption:
    """Adoption node model using direct Neo4j driver"""

    LABEL = "Adoption"

    def __init__(self, uid=None, date_adopted=None):
        self.uid = uid or self._generate_uid()
        if isinstance(date_adopted, (float, int)):
            # Assume it's a Unix timestamp
            self.date_adopted = datetime.fromtimestamp(date_adopted)
        else:
            self.date_adopted = date_adopted or datetime.now()

    def _generate_uid(self):
        """Generate a unique ID"""
        import uuid
        return str(uuid.uuid4())

    def save(self):
        """Save adoption node to database"""
        db = get_db()
        if not self.uid:
            self.uid = self._generate_uid()

        query = """
        MERGE (a:Adoption {uid: $uid})
        ON CREATE SET
            a.date_adopted = $date_adopted
        ON MATCH SET
            a.date_adopted = $date_adopted
        RETURN a
        """
        parameters = {
            "uid": self.uid,
            "date_adopted": self.date_adopted
        }

        result = db.execute_write(query, parameters)
        return result[0]["a"] if result else None

    @classmethod
    def get_by_uid(cls, uid):
        """Get adoption by UID"""
        db = get_db()
        query = """
        MATCH (a:Adoption {uid: $uid})
        RETURN a
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["a"]
            return cls(
                uid=record["uid"],
                date_adopted=record["date_adopted"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all adoptions"""
        db = get_db()
        query = """
        MATCH (a:Adoption)
        RETURN a
        """
        result = db.execute_query(query)
        adoptions = []
        for record in result:
            record_data = record["a"]
            adoptions.append(cls(
                uid=record_data["uid"],
                date_adopted=record_data["date_adopted"]
            ))
        return adoptions

    def farmer(self):
        """Get relationship to farmer (HAS_ADOPTED)"""
        db = get_db()
        query = """
        MATCH (a:Adoption {uid: $uid})-[:HAS_ADOPTED]->(f:Farmer)
        RETURN f
        """
        result = db.execute_query(query, {"uid": self.uid})
        from app.models.farmer import Farmer
        farmers = []
        for record in result:
            record_data = record["f"]
            farmers.append(Farmer(
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
        return farmers

    def input_product(self):
        """Get relationship to input product (IS_ADOPTED_BY)"""
        db = get_db()
        query = """
        MATCH (a:Adoption {uid: $uid})-[:IS_ADOPTED_BY]->(ip:InputProduct)
        RETURN ip
        """
        result = db.execute_query(query, {"uid": self.uid})
        from app.models.input_product.input_product import InputProduct
        products = []
        for record in result:
            record_data = record["ip"]
            products.append(InputProduct(
                name=record_data["name"],
                type_=record_data["type"],
                brand=record_data["brand"],
                cost=record_data["cost"],
                effectiveness_rating=record_data["effectiveness_rating"],
                uid=record_data["uid"]
            ))
        return products