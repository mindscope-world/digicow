"""Training Session Model"""
from neomodel import StructuredNode, StringProperty, DateTimeProperty, RelationshipFrom, RelationshipTo
from ..farmer import Farmer
from .training_topic import TrainingTopic
import uuid

class TrainingSession(StructuredNode):
    uid = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    title = StringProperty(required=True)
    description = StringProperty()
    session_date = DateTimeProperty(default_now=True)
    location = StringProperty()

    # Relationships
    participated_in = RelationshipFrom(Farmer, "PARTICIPATED_IN")
    conducted_by = RelationshipTo("app.models.trainer.trainer.Trainer", "TRAINS")
    covers = RelationshipTo(TrainingTopic, "COVERS")

    def __str__(self):
        return self.title