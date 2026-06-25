"""
Trainer Model using Direct Neo4j Driver
"""
from app.database import get_db

class Trainer:
    """Trainer node model using direct Neo4j driver"""

    LABEL = "Trainer"

    def __init__(self, name=None, specialty_areas=None, contact_info=None,
                 employee_id=None, uid=None):
        self.name = name
        self.specialty_areas = specialty_areas or ""
        self.contact_info = contact_info or ""
        self.employee_id = employee_id or (name.replace(" ", "_") if name else None)
        self.uid = uid

    def save(self):
        """Save trainer node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (t:Trainer {employee_id: $employee_id})
        ON CREATE SET
            t.uid = $uid,
            t.name = $name,
            t.specialty_areas = $specialty_areas,
            t.contact_info = $contact_info
        ON MATCH SET
            t.name = $name,
            t.specialty_areas = $specialty_areas,
            t.contact_info = $contact_info
        RETURN t
        """
        parameters = {
            "name": self.name,
            "specialty_areas": self.specialty_areas,
            "contact_info": self.contact_info,
            "employee_id": self.employee_id,
            "uid": self.uid
        }

        result = db.execute_write(query, parameters)
        return result[0]["t"] if result else None

    @classmethod
    def get_by_employee_id(cls, employee_id):
        """Get trainer by employee_id"""
        db = get_db()
        query = """
        MATCH (t:Trainer {employee_id: $employee_id})
        RETURN t
        """
        result = db.execute_query(query, {"employee_id": employee_id})
        if result:
            record = result[0]["t"]
            return cls(
                name=record["name"],
                specialty_areas=record["specialty_areas"],
                contact_info=record["contact_info"],
                employee_id=record["employee_id"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_uid(cls, uid):
        """Get trainer by UID"""
        db = get_db()
        query = """
        MATCH (t:Trainer {uid: $uid})
        RETURN t
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["t"]
            return cls(
                name=record["name"],
                specialty_areas=record["specialty_areas"],
                contact_info=record["contact_info"],
                employee_id=record["employee_id"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all trainers"""
        db = get_db()
        query = """
        MATCH (t:Trainer)
        RETURN t
        """
        result = db.execute_query(query)
        trainers = []
        for record in result:
            record_data = record["t"]
            trainers.append(cls(
                name=record_data["name"],
                specialty_areas=record_data["specialty_areas"],
                contact_info=record_data["contact_info"],
                employee_id=record_data["employee_id"],
                uid=record_data["uid"]
            ))
        return trainers

    def farmers(self):
        """Get relationship to farmers (trains)"""
        db = get_db()
        query = """
        MATCH (t:Trainer {employee_id: $employee_id})-[:TRAINED_BY]->(f:Farmer)
        RETURN f
        """
        result = db.execute_query(query, {"employee_id": self.employee_id})
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

    def topics(self):
        """Get relationship to training topics (specializes_in)"""
        db = get_db()
        query = """
        MATCH (t:Trainer {employee_id: $employee_id})-[:SPECIALIZES_IN]->(topic:TrainingTopic)
        RETURN topic
        """
        result = db.execute_query(query, {"employee_id": self.employee_id})
        from app.models.training.training_topic import TrainingTopic
        topics = []
        for record in result:
            record_data = record["topic"]
            topics.append(TrainingTopic(
                name=record_data["name"],
                category=record_data["category"],
                description=record_data["description"],
                uid=record_data["uid"]
            ))
        return topics

    def trainings_conducted(self):
        """Get relationship to training sessions conducted"""
        db = get_db()
        query = """
        MATCH (t:Trainer {employee_id: $employee_id})-[:CONDUCTED_BY]->(ts:TrainingSession)
        RETURN ts
        """
        result = db.execute_query(query, {"employee_id": self.employee_id})
        from app.models.training import TrainingSession
        trainings = []
        for record in result:
            record_data = record["ts"]
            trainings.append(TrainingSession(
                title=record_data["title"],
                description=record_data["description"],
                session_date=record_data["session_date"],
                location=record_data["location"],
                uid=record_data["uid"]
            ))
        return trainings