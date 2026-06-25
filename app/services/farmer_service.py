"""
Farmer Service Layer using Direct Neo4j Driver
"""
import os
from typing import List, Optional
from datetime import datetime
from app.models.farmer import Farmer
from app.models.cooperative import Cooperative
from app.models.location.ward import Ward
from app.models.trainer.trainer import Trainer
from app.models.training import TrainingSession
from app.models.adoption import Adoption
from app.models.advisory.advisory import AdvisoryRecommendation
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse, FarmerProfileResponse
from app.database import get_db


class FarmerService:
    """
    Service class for Farmer operations using direct Neo4j driver
    """

    @staticmethod
    def _load_farmers_from_csv() -> List[Farmer]:
        """Load farmers from CSV file and convert to Farmer objects."""
        farmers = []
        csv_path = "/home/mindscope/Lab/hackathons/backend/data/Prior_digicow.csv"

        if not os.path.exists(csv_path):
            return farmers

        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Skip empty rows
                if not row.get('ID'):
                    continue

                # Map CSV fields to Farmer model fields
                farmer_data = {
                    'farmer_id': row['ID'],
                    'gender': row['gender'],
                    'age_bracket': row['age'],  # CSV 'age' column maps to age_bracket
                    'registration_method': row['registration'],
                    'belongs_to_cooperative': bool(int(row['belong_to_cooperative'])),
                    # Default values for fields not in CSV
                    'phone': None,
                    'herd_size': 0,
                    'acres_under_cultivation': 0.0,
                    'primary_enterprise': None,
                }

                # Create Farmer instance and save to DB
                farmer = Farmer(**farmer_data)
                farmer.save()
                farmers.append(farmer)

        return farmers

    @staticmethod
    async def create_farmer(farmer_data: FarmerCreate) -> FarmerResponse:
        """
        Create a new farmer
        """
        # Check if farmer already exists
        existing_farmer = Farmer.get_by_id(farmer_data.farmer_id)
        if existing_farmer:
            raise ValueError(f"Farmer with ID {farmer_data.farmer_id} already exists")

        # Create new farmer
        farmer = Farmer(**farmer_data.dict())
        farmer.save()

        return FarmerResponse.from_orm(farmer)

    @staticmethod
    async def get_farmer(farmer_id: str) -> Optional[FarmerResponse]:
        """
        Get a farmer by ID
        """
        farmer = Farmer.get_by_id(farmer_id)
        if not farmer:
            return None

        return FarmerResponse.from_orm(farmer)

    @staticmethod
    async def get_farmers(
        skip: int = 0,
        limit: int = 100,
        gender: Optional[str] = None,
        age_bracket: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[FarmerResponse]:
        """
        Get list of farmers with filtering and pagination from database
        """
        # Get all farmers from database
        all_farmers = Farmer.all()

        # Apply filters
        filtered_farmers = []
        for farmer in all_farmers:
            if gender and farmer.gender != gender:
                continue
            if age_bracket and farmer.age_bracket != age_bracket:
                continue
            # Note: status filtering would require storing status in DB
            # For now, we'll skip status filtering as it's not in the CSV data
            filtered_farmers.append(farmer)

        # Apply pagination
        paginated_farmers = filtered_farmers[skip:skip + limit]

        # Convert to FarmerResponse objects
        return [FarmerResponse.from_orm(farmer) for farmer in paginated_farmers]

    @staticmethod
    async def update_farmer(farmer_id: str, farmer_data: FarmerUpdate) -> Optional[FarmerResponse]:
        """
        Update an existing farmer
        """
        farmer = Farmer.get_by_id(farmer_id)
        if not farmer:
            return None

        # Update fields
        update_data = farmer_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(farmer, field, value)

        # Update timestamp - in a real implementation, we'd have an updated_at field
        # For now, we'll just save the farmer
        farmer.save()

        return FarmerResponse.from_orm(farmer)

    @staticmethod
    async def deactivate_farmer(farmer_id: str) -> bool:
        """
        Deactivate a farmer (soft delete)
        """
        farmer = Farmer.get_by_id(farmer_id)
        if not farmer:
            return False

        # In a real implementation, we'd have a status field in the database
        # For now, we'll just return True to simulate the operation
        # A proper implementation would update a status property in the database
        return True

    @staticmethod
    async def get_farmer_profile_with_relationships(farmer_id: str) -> Optional[FarmerProfileResponse]:
        """
        Get detailed farmer profile with relationships using direct Cypher queries
        """
        farmer = Farmer.get_by_id(farmer_id)
        if not farmer:
            return None

        db = get_db()

        # Initialize lists for relationship data
        member_of = []
        located_in = None
        trained_by = []
        participated_in = []
        has_adopted = []
        receives = []

        # Fetch cooperatives (member_of)
        try:
            query = """
            MATCH (f:Farmer {farmer_id: $farmer_id})-[:MEMBER_OF]->(c:Cooperative)
            RETURN c.name as name
            """
            result = db.execute_query(query, {"farmer_id": farmer_id})
            member_of = [record["name"] for record in result]
        except Exception:
            pass  # If there's an error, leave as empty list

        # Fetch ward (located_in)
        try:
            query = """
            MATCH (f:Farmer {farmer_id: $farmer_id})-[:LOCATED_IN]->(w:Ward)
            RETURN w.name as name, w.code as code
            """
            result = db.execute_query(query, {"farmer_id": farmer_id})
            if result:
                record = result[0]
                located_in = f"{record['name']} ({record['code']})" if record['code'] else record['name']
        except Exception:
            pass  # If there's an error, leave as None

        # Fetch trainers (trained_by)
        try:
            query = """
            MATCH (f:Farmer {farmer_id: $farmer_id})-[:TRAINED_BY]->(t:Trainer)
            RETURN t.name as name
            """
            result = db.execute_query(query, {"farmer_id": farmer_id})
            trained_by = [record["name"] for record in result]
        except Exception:
            pass

        # Fetch training sessions (attended_by)
        try:
            query = """
            MATCH (f:Farmer {farmer_id: $farmer_id})-[:ATTENDED_BY]->(ts:TrainingSession)
            RETURN ts.title as title
            """
            result = db.execute_query(query, {"farmer_id": farmer_id})
            participated_in = [record["title"] for record in result if record["title"]]
        except Exception:
            pass

        # Fetch input products (has_adopted)
        try:
            query = """
            MATCH (f:Farmer {farmer_id: $farmer_id})-[:HAS_ADOPTED]->(a:Adoption)-[:INPUT_PRODUCT]->(ip:InputProduct)
            RETURN ip.name as name
            """
            result = db.execute_query(query, {"farmer_id": farmer_id})
            has_adopted = [record["name"] for record in result]
        except Exception:
            pass

        # Fetch advisory recommendations (receives)
        try:
            query = """
            MATCH (f:Farmer {farmer_id: $farmer_id})-[:RECEIVES]->(ar:AdvisoryRecommendation)
            RETURN ar.recommendation_type as type, ar.advice as advice
            """
            result = db.execute_query(query, {"farmer_id": farmer_id})
            receives = [
                f"{record['type']}: {record['advice'][:50]}..." if record['advice'] and len(record['advice']) > 50
                else f"{record['type']}: {record['advice']}"
                for record in result
            ]
        except Exception:
            pass

        # Create the base farmer response
        farmer_response = FarmerResponse.from_orm(farmer)

        # Create and return the profile response
        return FarmerProfileResponse(
            **farmer_response.dict(),
            member_of=member_of,
            located_in=located_in,
            trained_by=trained_by,
            participated_in=participated_in,
            has_adopted=has_adopted,
            receives=receives
        )