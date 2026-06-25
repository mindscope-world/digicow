"""
Farmer Model using Direct Neo4j Driver
"""
from app.database import get_db
from datetime import datetime

class Farmer:
    """Farmer node model using direct Neo4j driver"""

    LABEL = "Farmer"

    def __init__(self, farmer_id=None, gender=None, age_bracket=None,
                 registration_method=None, belongs_to_cooperative=False,
                 phone=None, herd_size=0, acres_under_cultivation=0.0,
                 primary_enterprise=None, uid=None, created_at=None,
                 updated_at=None, last_contact=None,
                 engagement_score_7d=0, engagement_score_30d=0,
                 engagement_score_90d=0, trend="flat", status="Active"):
        self.farmer_id = farmer_id
        self.gender = gender
        self.age_bracket = age_bracket
        self.registration_method = registration_method
        self.belongs_to_cooperative = belongs_to_cooperative
        self.phone = phone
        self.herd_size = herd_size
        self.acres_under_cultivation = acres_under_cultivation
        self.primary_enterprise = primary_enterprise
        self.uid = uid
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at
        self.last_contact = last_contact
        self.engagement_score_7d = engagement_score_7d
        self.engagement_score_30d = engagement_score_30d
        self.engagement_score_90d = engagement_score_90d
        self.trend = trend
        self.status = status

    def save(self):
        """Save farmer node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (f:Farmer {farmer_id: $farmer_id})
        ON CREATE SET
            f.uid = $uid,
            f.gender = $gender,
            f.age_bracket = $age_bracket,
            f.registration_method = $registration_method,
            f.belongs_to_cooperative = $belongs_to_cooperative,
            f.phone = $phone,
            f.herd_size = $herd_size,
            f.acres_under_cultivation = $acres_under_cultivation,
            f.primary_enterprise = $primary_enterprise
        ON MATCH SET
            f.gender = $gender,
            f.age_bracket = $age_bracket,
            f.registration_method = $registration_method,
            f.belongs_to_cooperative = $belongs_to_cooperative,
            f.phone = $phone,
            f.herd_size = $herd_size,
            f.acres_under_cultivation = $acres_under_cultivation,
            f.primary_enterprise = $primary_enterprise
        RETURN f
        """
        parameters = {
            "farmer_id": self.farmer_id,
            "uid": self.uid,
            "gender": self.gender,
            "age_bracket": self.age_bracket,
            "registration_method": self.registration_method,
            "belongs_to_cooperative": self.belongs_to_cooperative,
            "phone": self.phone,
            "herd_size": self.herd_size,
            "acres_under_cultivation": self.acres_under_cultivation,
            "primary_enterprise": self.primary_enterprise
        }

        result = db.execute_write(query, parameters)
        return result[0]["f"] if result else None

    @classmethod
    def get_by_id(cls, farmer_id):
        """Get farmer by farmer_id"""
        db = get_db()
        query = """
        MATCH (f:Farmer {farmer_id: $farmer_id})
        RETURN f
        """
        result = db.execute_query(query, {"farmer_id": farmer_id})
        if result:
            record = result[0]["f"]
            return cls(
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

    @classmethod
    def get_by_uid(cls, uid):
        """Get farmer by UID"""
        db = get_db()
        query = """
        MATCH (f:Farmer {uid: $uid})
        RETURN f
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["f"]
            return cls(
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

    @classmethod
    def all(cls):
        """Get all farmers"""
        db = get_db()
        query = """
        MATCH (f:Farmer)
        RETURN f
        """
        result = db.execute_query(query)
        farmers = []
        for record in result:
            record_data = record["f"]
            farmers.append(cls(
                farmer_id=record_data["farmer_id"],
                gender=record_data["gender"],
                age_bracket=record_data["age_bracket"],
                registration_method=record_data["registration_method"],
                belongs_to_cooperative=record_data["belongs_to_cooperative"],
                phone=record_data["phone"],
                herd_size=record_data["herd_size"],
                acres_under_cultivation=record_data["acres_under_cultivation"],
                primary_enterprise=record_data["primary_enterprise"],
                uid=record_data["uid"],
                created_at=record_data.get("created_at"),
                updated_at=record_data.get("updated_at"),
                last_contact=record_data.get("last_contact"),
                engagement_score_7d=record_data.get("engagement_score_7d", 0),
                engagement_score_30d=record_data.get("engagement_score_30d", 0),
                engagement_score_90d=record_data.get("engagement_score_90d", 0),
                trend=record_data.get("trend", "flat"),
                status=record_data.get("status", "Active")
            ))
        return farmers

    def located_in(self, ward):
        """Create relationship to ward"""
        db = get_db()
        query = """
        MATCH (f:Farmer {farmer_id: $farmer_id})
        MATCH (w:Ward {code: $ward_code})
        MERGE (f)-[:LOCATED_IN]->(w)
        """
        db.execute_write(query, {
            "farmer_id": self.farmer_id,
            "ward_code": ward.code
        })

    def trained_by(self, trainer):
        """Create relationship to trainer"""
        db = get_db()
        query = """
        MATCH (f:Farmer {farmer_id: $farmer_id})
        MATCH (t:Trainer {employee_id: $trainer_id})
        MERGE (f)-[:TRAINED_BY]->(t)
        """
        db.execute_write(query, {
            "farmer_id": self.farmer_id,
            "trainer_id": trainer.employee_id
        })

    def attended_by(self, training_session):
        """Create relationship to training session"""
        db = get_db()
        query = """
        MATCH (f:Farmer {farmer_id: $farmer_id})
        MATCH (t:TrainingSession {uid: $session_uid})
        MERGE (f)-[:ATTENDED_BY]->(t)
        """
        db.execute_write(query, {
            "farmer_id": self.farmer_id,
            "session_uid": training_session.uid
        })

    def member_of(self, cooperative):
        """Create relationship to cooperative"""
        db = get_db()
        query = """
        MATCH (f:Farmer {farmer_id: $farmer_id})
        MATCH (c:Cooperative {name: $coop_name})
        MERGE (f)-[:MEMBER_OF]->(c)
        """
        db.execute_write(query, {
            "farmer_id": self.farmer_id,
            "coop_name": cooperative.name
        })

    def participated_in(self, training_session):
        """Create relationship to training session (alternative to attended_by)"""
        return self.attended_by(training_session)

    def has_adopted(self, adoption):
        """Create relationship to adoption"""
        db = get_db()
        query = """
        MATCH (f:Farmer {farmer_id: $farmer_id})
        MATCH (a:Adoption {uid: $adoption_uid})
        MERGE (f)-[:HAS_ADOPTED]->(a)
        """
        db.execute_write(query, {
            "farmer_id": self.farmer_id,
            "adoption_uid": adoption.uid
        })

    def receives(self, advisory):
        """Create relationship to advisory recommendation"""
        db = get_db()
        query = """
        MATCH (f:Farmer {farmer_id: $farmer_id})
        MATCH (a:AdvisoryRecommendation {uid: $advisory_uid})
        MERGE (f)-[:RECEIVES]->(a)
        """
        db.execute_write(query, {
            "farmer_id": self.farmer_id,
            "advisory_uid": advisory.uid
        })

    def located_in_ward(self):
        """Get the ward this farmer is located in"""
        db = get_db()
        query = """
        MATCH (f:Farmer {farmer_id: $farmer_id})-[:LOCATED_IN]->(w:Ward)
        RETURN w
        """
        result = db.execute_query(query, {"farmer_id": self.farmer_id})
        if result:
            from app.models.location.ward import Ward
            record = result[0]["w"]
            return Ward(
                name=record["name"],
                code=record["code"],
                uid=record["uid"]
            )
        return None