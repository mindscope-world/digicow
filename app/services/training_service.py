"""
Training Service Layer using Direct Neo4j Driver
"""
from typing import List, Optional
from datetime import datetime
from app.models.training import TrainingSession
from app.models.trainer.trainer import Trainer
from app.models.training.training_topic import TrainingTopic
from app.models.farmer import Farmer
from app.schemas.training import TrainingSessionCreate, TrainingSessionResponse
from app.database import get_db


class TrainingService:
    """
    Service class for Training operations using direct Neo4j driver
    """

    @staticmethod
    async def create_training_session(training_data: TrainingSessionCreate) -> TrainingSessionResponse:
        """
        Create a new training session
        """
        # Create the training session instance
        training_session = TrainingSession(
            title=training_data.title,
            description=training_data.description,
            session_date=training_data.session_date,
            location=training_data.location
        )
        training_session.save()

        # If trainer IDs are provided, connect them
        if training_data.trainer_ids:
            for trainer_id in training_data.trainer_ids:
                trainer = Trainer.get_by_employee_id(trainer_id)
                if trainer:
                    # Create relationship: TrainingSession -[CONDUCTED_BY]-> Trainer
                    db = get_db()
                    query = """
                    MATCH (ts:TrainingSession {uid: $session_uid})
                    MATCH (t:Trainer {employee_id: $trainer_id})
                    MERGE (ts)-[:CONDUCTED_BY]->(t)
                    """
                    db.execute_write(query, {
                        "session_uid": training_session.uid,
                        "trainer_id": trainer_id
                    })

        # If topic IDs are provided, connect them
        if training_data.topic_ids:
            for topic_name in training_data.topic_ids:
                topic = TrainingTopic.get_by_name(topic_name)
                if topic:
                    # Create relationship: TrainingSession -[HAS_TOPIC]-> TrainingTopic
                    db = get_db()
                    query = """
                    MATCH (ts:TrainingSession {uid: $session_uid})
                    MATCH (t:TrainingTopic {name: $topic_name})
                    MERGE (ts)-[:HAS_TOPIC]->(t)
                    """
                    db.execute_write(query, {
                        "session_uid": training_session.uid,
                        "topic_name": topic_name
                    })

        # Refresh the instance to get relationships (not needed with direct driver approach)
        # In direct driver approach, we'll fetch fresh data when needed

        # Prepare response
        return TrainingSessionResponse(
            id=str(training_session.uid),
            title=training_session.title,
            description=training_session.description,
            session_date=training_session.session_date,
            location=training_session.location,
            trainer_ids=training_data.trainer_ids or [],
            topic_ids=training_data.topic_ids or [],
            conducted_by=[t.name for t in TrainingService._get_session_trainers(training_session.uid)],
            covers=[t.name for t in TrainingService._get_session_topics(training_session.uid)],
            participated_in=[f.farmer_id for f in TrainingService._get_session_attendees(training_session.uid)]
        )

    @staticmethod
    async def get_training_session(session_id: str) -> Optional[TrainingSessionResponse]:
        """
        Get a training session by ID
        """
        training_session = TrainingSession.get_by_uid(session_id)
        if not training_session:
            return None

        return TrainingSessionResponse(
            id=str(training_session.uid),
            title=training_session.title,
            description=training_session.description,
            session_date=training_session.session_date,
            location=training_session.location,
            trainer_ids=[t.employee_id for t in TrainingService._get_session_trainers(session_id)],
            topic_ids=[t.name for t in TrainingService._get_session_topics(session_id)],
            conducted_by=[t.name for t in TrainingService._get_session_trainers(session_id)],
            covers=[t.name for t in TrainingService._get_session_topics(session_id)],
            participated_in=[f.farmer_id for f in TrainingService._get_session_attendees(session_id)]
        )

    @staticmethod
    async def list_training_sessions(
        skip: int = 0,
        limit: int = 100,
        title: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TrainingSessionResponse]:
        """
        List training sessions with filtering and pagination using direct Cypher queries
        """
        db = get_db()

        # Build the base query
        query = """
        MATCH (ts:TrainingSession)
        """
        params = {}

        # Add filters
        conditions = []
        if title:
            conditions.append("ts.title CONTAINS $title")
            params["title"] = title
        if location:
            conditions.append("ts.location CONTAINS $location")
            params["location"] = location
        if start_date:
            conditions.append("ts.session_date >= $start_date")
            params["start_date"] = start_date
        if end_date:
            conditions.append("ts.session_date <= $end_date")
            params["end_date"] = end_date

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Add ordering and pagination
        query += """
        ORDER BY ts.session_date DESC
        SKIP $skip
        LIMIT $limit
        """
        params["skip"] = skip
        params["limit"] = limit

        # Execute query
        result = db.execute_query(query, params)

        # Convert to response objects
        results = []
        for record in result:
            session_data = record["ts"]
            session = TrainingSession(
                title=session_data["title"],
                description=session_data["description"],
                session_date=session_data["session_date"],
                location=session_data["location"],
                uid=session_data["uid"]
            )

            results.append(TrainingSessionResponse(
                id=str(session.uid),
                title=session.title,
                description=session.description,
                session_date=session.session_date,
                location=session.location,
                trainer_ids=[t.employee_id for t in TrainingService._get_session_trainers(session.uid)],
                topic_ids=[t.name for t in TrainingService._get_session_topics(session.uid)],
                conducted_by=[t.name for t in TrainingService._get_session_trainers(session.uid)],
                covers=[t.name for t in TrainingService._get_session_topics(session.uid)],
                participated_in=[f.farmer_id for f in TrainingService._get_session_attendees(session.uid)]
            ))
        return results

    @staticmethod
    def _get_session_trainers(session_uid: str) -> List[Trainer]:
        """Get trainers for a training session"""
        db = get_db()
        query = """
        MATCH (ts:TrainingSession {uid: $session_uid})-[:CONDUCTED_BY]->(t:Trainer)
        RETURN t
        """
        result = db.execute_query(query, {"session_uid": session_uid})
        trainers = []
        for record in result:
            trainer_data = record["t"]
            trainers.append(Trainer(
                name=trainer_data["name"],
                specialty_areas=trainer_data["specialty_areas"],
                contact_info=trainer_data["contact_info"],
                employee_id=trainer_data["employee_id"],
                uid=trainer_data["uid"]
            ))
        return trainers

    @staticmethod
    def _get_session_topics(session_uid: str) -> List[TrainingTopic]:
        """Get topics for a training session"""
        db = get_db()
        query = """
        MATCH (ts:TrainingSession {uid: $session_uid})-[:HAS_TOPIC]->(t:TrainingTopic)
        RETURN t
        """
        result = db.execute_query(query, {"session_uid": session_uid})
        topics = []
        for record in result:
            topic_data = record["t"]
            topics.append(TrainingTopic(
                name=topic_data["name"],
                category=topic_data["category"],
                description=topic_data["description"],
                uid=topic_data["uid"]
            ))
        return topics

    @staticmethod
    def _get_session_attendees(session_uid: str) -> List[Farmer]:
        """Get attendees for a training session"""
        db = get_db()
        query = """
        MATCH (ts:TrainingSession {uid: $session_uid})<-[:ATTENDED_BY]-(f:Farmer)
        RETURN f
        """
        result = db.execute_query(query, {"session_uid": session_uid})
        farmers = []
        for record in result:
            farmer_data = record["f"]
            farmers.append(Farmer(
                farmer_id=farmer_data["farmer_id"],
                gender=farmer_data["gender"],
                age_bracket=farmer_data["age_bracket"],
                registration_method=farmer_data["registration_method"],
                belongs_to_cooperative=farmer_data["belongs_to_cooperative"],
                phone=farmer_data["phone"],
                herd_size=farmer_data["herd_size"],
                acres_under_cultivation=farmer_data["acres_under_cultivation"],
                primary_enterprise=farmer_data["primary_enterprise"],
                uid=farmer_data["uid"]
            ))
        return farmers