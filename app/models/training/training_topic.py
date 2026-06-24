"""Training Topic Model"""
from neomodel import StructuredNode, StringProperty, UniqueIdProperty


class TrainingTopic(StructuredNode):
    name = StringProperty(required=True, unique_index=True)
    description = StringProperty()

    def __str__(self):
        return self.name