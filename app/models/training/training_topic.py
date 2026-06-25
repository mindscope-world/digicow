"""
Training Topic Model using Direct Neo4j Driver
"""
from app.database import get_db

class TrainingTopic:
    """TrainingTopic node model using direct Neo4j driver"""

    LABEL = "TrainingTopic"

    def __init__(self, name=None, category=None, description=None, uid=None):
        self.name = name
        self.category = category or ""
        self.description = description or ""
        self.uid = uid

    def save(self):
        """Save training topic node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (t:TrainingTopic {name: $name})
        ON CREATE SET
            t.uid = $uid,
            t.category = $category,
            t.description = $description
        ON MATCH SET
            t.category = $category,
            t.description = $description
        RETURN t
        """
        parameters = {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "uid": self.uid
        }

        result = db.execute_write(query, parameters)
        return result[0]["t"] if result else None

    @classmethod
    def get_by_name(cls, name):
        """Get training topic by name"""
        db = get_db()
        query = """
        MATCH (t:TrainingTopic {name: $name})
        RETURN t
        """
        result = db.execute_query(query, {"name": name})
        if result:
            record = result[0]["t"]
            return cls(
                name=record["name"],
                category=record["category"],
                description=record["description"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_uid(cls, uid):
        """Get training topic by UID"""
        db = get_db()
        query = """
        MATCH (t:TrainingTopic {uid: $uid})
        RETURN t
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["t"]
            return cls(
                name=record["name"],
                category=record["category"],
                description=record["description"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all training topics"""
        db = get_db()
        query = """
        MATCH (t:TrainingTopic)
        RETURN t
        """
        result = db.execute_query(query)
        topics = []
        for record in result:
            record_data = record["t"]
            topics.append(cls(
                name=record_data["name"],
                category=record_data["category"],
                description=record_data["description"],
                uid=record_data["uid"]
            ))
        return topics

    def trainers(self):
        """Get relationship to trainers (specializes_in)"""
        db = get_db()
        query = """
        MATCH (t:TrainingTopic {name: $name})<-[:SPECIALIZES_IN]-(trainer:Trainer)
        RETURN trainer
        """
        result = db.execute_query(query, {"name": self.name})
        from app.models.trainer.trainer import Trainer
        trainers = []
        for record in result:
            record_data = record["trainer"]
            trainers.append(Trainer(
                name=record_data["name"],
                specialty_areas=record_data["specialty_areas"],
                contact_info=record_data["contact_info"],
                employee_id=record_data["employee_id"],
                uid=record_data["uid"]
            ))
        return trainers

    def training_sessions(self):
        """Get relationship to training sessions (has_topic)"""
        db = get_db()
        query = """
        MATCH (t:TrainingTopic {name: $name})<-[:HAS_TOPIC]-(ts:TrainingSession)
        RETURN ts
        """
        result = db.execute_query(query, {"name": self.name})
        from app.models.training import TrainingSession
        sessions = []
        for record in result:
            record_data = record["ts"]
            sessions.append(TrainingSession(
                title=record_data["title"],
                description=record_data["description"],
                session_date=record_data["session_date"],
                location=record_data["location"],
                duration=record_data["duration"],
                attendance_count=record_data["attendance_count"],
                uid=record_data["uid"]
            ))
        return sessions