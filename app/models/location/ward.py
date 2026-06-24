"""Ward Model"""
from neomodel import StructuredNode, StringProperty, RelationshipFrom, RelationshipTo


# Actually we need to define Ward class. We'll also need County and Subcounty for relationships if needed.
# For simplicity, we'll just define Ward with a name and maybe a code.
# We'll also add relationships to Subcounty and County if we want, but not required for now.

class Ward(StructuredNode):
    name = StringProperty(required=True)
    code = StringProperty(unique_index=True)

    # Relationships (optional)
    # belongs_to_subcounty = RelationshipFrom("location.Subcounty", "LOCATED_IN")
    # Contains villages? Not needed.

    def __str__(self):
        return f"{self.name} ({self.code})"