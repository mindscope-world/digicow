"""
Training Session Model using Direct Neo4j Driver
"""
from app.database import get_db
from datetime import datetime

class TrainingSession:
    """TrainingSession node model using direct Neo4j driver"""

    LABEL = "TrainingSession"

    def __init__(self, title=None, description=None, session_date=None,
                 location=None, duration=None, attendance_count=0, uid=None):
        self.title = title
        self.description = description
        if isinstance(session_date, (float, int)):
            # Assume it's a Unix timestamp
            self.session_date = datetime.fromtimestamp(session_date)
        else:
            self.session_date = session_date or datetime.now()
        self.location = location
        self.duration = duration or 2  # default 2 hours
        self.attendance_count = attendance_count
        self.uid = uid

    def save(self):
        """Save training session node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (ts:TrainingSession {uid: $uid})
        ON CREATE SET
            ts.title = $title,
            ts.description = $description,
            ts.session_date = $session_date,
            ts.location = $location,
            ts.duration = $duration,
            ts.attendance_count = $attendance_count
        ON MATCH SET
            ts.title = $title,
            ts.description = $description,
            ts.session_date = $session_date,
            ts.location = $location,
            ts.duration = $duration,
            ts.attendance_count = $attendance_count
        RETURN ts
        """
        parameters = {
            "title": self.title,
            "description": self.description,
            "session_date": self.session_date,
            "location": self.location,
            "duration": self.duration,
            "attendance_count": self.attendance_count,
            "uid": self.uid
        }

        result = db.execute_write(query, parameters)
        return result[0]["ts"] if result else None

    @classmethod
    def get_by_uid(cls, uid):
        """Get training session by UID"""
        db = get_db()
        query = """
        MATCH (ts:TrainingSession {uid: $uid})
        RETURN ts
        """
        result = db.execute_query(query, {"uid": uid })
        if result:
            record = result[0]["ts"]
            return cls(
                title=record["title"],
                description=record["description"],
                session_date=record["session_date"],
                location=record["location"],
                duration=record["duration"],
                attendance_count=record["attendance_count"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all training sessions"""
        db = get_db()
        query = """
        MATCH (ts:TrainingSession)
        RETURN ts
        """
        result = db.execute_query(query)
        sessions = []
        for record in result:
            record_data = record["ts"]
            sessions.append(cls(
                title=record_data["title"],
                description=record_data["description"],
                session_date=record_data["session_date"],
                location=record_data["location"],
                duration=record_data["duration"],
                attendance_count=record_data["attendance_count"],
                uid=record_data["uid"]
            ))
        return sessions

    def topics(self):
        """Get relationship to training topics (has_topic)"""
        db = get_db()
        query = """
        MATCH (ts:TrainingSession {uid: $uid})-[:HAS_TOPIC]->(topic:TrainingTopic)
        RETURN topic
        """
        result = db.execute_query(query, {"uid": self.uid})
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

    def trainers(self):
        """Get relationship to trainers (conducted_by)"""
        db = get_db()
        query = """
        MATCH (ts:TrainingSession {uid: $uid})-[:CONDUCTED_BY]->(trainer:Trainer)
        RETURN trainer
        """
        result = db.execute_query(query, {"uid": self.uid})
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

    def attendees(self):
        """Get relationship to farmers (attended_by)"""
        db = get_db()
        query = """
        MATCH (ts:TrainingSession {uid: $uid})<-[:ATTENDED_BY]-(farmer:Farmer)
        RETURN farmer
        """
        result = db.execute_query(query, {"uid": self.uid})
        from app.models.farmer import Farmer
        farmers = []
        for record in result:
            record_data = record["farmer"]
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