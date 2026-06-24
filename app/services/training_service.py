"""
Training Service Layer
"""
from typing import List, Optional
from datetime import datetime
from ..models.trainer.trainer import Trainer
from ..models.training.training_topic import TrainingTopic
from app.models.training import TrainingSession
from app.schemas.training import TrainingSessionCreate, TrainingSessionResponse


class TrainingService:
    """
    Service class for Training operations
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
            trainers = Trainer.nodes.filter(employee_id__in=training_data.trainer_ids)
            for trainer in trainers:
                training_session.conducted_by.connect(trainer)

        # If topic IDs are provided, connect them
        if training_data.topic_ids:
            topics = TrainingTopic.nodes.filter(name__in=training_data.topic_ids)
            for topic in topics:
                training_session.covers.connect(topic)

        # Refresh the instance to get relationships
        training_session.refresh()

        # Prepare response
        return TrainingSessionResponse(
            id=str(training_session.uid),
            title=training_session.title,
            description=training_session.description,
            session_date=training_session.session_date,
            location=training_session.location,
            trainer_ids=training_data.trainer_ids,
            topic_ids=training_data.topic_ids,
            conducted_by=[trainer.name for trainer in training_session.conducted_by.all()],
            covers=[topic.name for topic in training_session.covers.all()],
            participated_in=[farmer.farmer_id for farmer in training_session.participated_in.all()]
        )

    @staticmethod
    async def get_training_session(session_id: str) -> Optional[TrainingSessionResponse]:
        """
        Get a training session by ID
        """
        training_session = TrainingSession.nodes.get_or_none(uid=session_id)
        if not training_session:
            return None

        return TrainingSessionResponse(
            id=str(training_session.uid),
            title=training_session.title,
            description=training_session.description,
            session_date=training_session.session_date,
            location=training_session.location,
            trainer_ids=[t.employee_id for t in training_session.conducted_by.all()],
            topic_ids=[t.name for t in training_session.covers.all()],
            conducted_by=[trainer.name for trainer in training_session.conducted_by.all()],
            covers=[topic.name for topic in training_session.covers.all()],
            participated_in=[farmer.farmer_id for farmer in training_session.participated_in.all()]
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
        List training sessions with filtering and pagination
        """
        query = TrainingSession.nodes

        # Apply filters
        if title:
            query = query.filter(title__icontains=title)
        if location:
            query = query.filter(location__icontains=location)
        if start_date:
            query = query.filter(session_date__gte=start_date)
        if end_date:
            query = query.filter(session_date__lte=end_date)

        # Apply pagination
        training_sessions = query[skip:skip + limit]

        # Convert to response objects
        results = []
        for session in training_sessions:
            results.append(TrainingSessionResponse(
                id=str(session.uid),
                title=session.title,
                description=session.description,
                session_date=session.session_date,
                location=session.location,
                trainer_ids=[t.employee_id for t in session.conducted_by.all()],
                topic_ids=[t.name for t in session.covers.all()],
                conducted_by=[trainer.name for trainer in session.conducted_by.all()],
                covers=[topic.name for topic in session.covers.all()],
                participated_in=[farmer.farmer_id for farmer in session.participated_in.all()]
            ))
        return results