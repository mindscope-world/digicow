"""
Farmer Service Layer
"""
import csv
import os
from typing import List, Optional
from datetime import datetime
from app.models.farmer import Farmer
from app.models.cooperative import Cooperative
from app.models.location.ward import Ward
from app.models.trainer import Trainer
from app.models.training import TrainingSession
from app.models.input_product import InputProduct
from app.models.advisory import AdvisoryRecommendation
from app.schemas.farmer import FarmerCreate, FarmerUpdate, FarmerResponse, FarmerProfileResponse


class FarmerService:
    """
    Service class for Farmer operations
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

                # Create Farmer instance (don't save to DB, just for in-memory use)
                farmer = Farmer(**farmer_data)
                farmers.append(farmer)

        return farmers

    @staticmethod
    async def create_farmer(farmer_data: FarmerCreate) -> FarmerResponse:
        """
        Create a new farmer
        """
        # Check if farmer already exists
        existing_farmer = Farmer.nodes.get_or_none(farmer_id=farmer_data.farmer_id)
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
        farmer = Farmer.nodes.get_or_none(farmer_id=farmer_id)
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
        Get list of farmers with filtering and pagination from CSV
        """
        # Load all farmers from CSV
        all_farmers = FarmerService._load_farmers_from_csv()

        # Apply filters
        filtered_farmers = []
        for farmer in all_farmers:
            if gender and farmer.gender != gender:
                continue
            if age_bracket and farmer.age_bracket != age_bracket:
                continue
            if status and farmer.status != status:
                continue
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
        farmer = Farmer.nodes.get_or_none(farmer_id=farmer_id)
        if not farmer:
            return None

        # Update fields
        update_data = farmer_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(farmer, field, value)

        # Update timestamp
        farmer.updated_at = datetime.now()
        farmer.save()

        return FarmerResponse.from_orm(farmer)

    @staticmethod
    async def deactivate_farmer(farmer_id: str) -> bool:
        """
        Deactivate a farmer (soft delete)
        """
        farmer = Farmer.nodes.get_or_none(farmer_id=farmer_id)
        if not farmer:
            return False

        farmer.status = "Dormant"
        farmer.updated_at = datetime.now()
        farmer.save()

        return True

    @staticmethod
    async def get_farmer_profile_with_relationships(farmer_id: str) -> Optional[FarmerProfileResponse]:
        """
        Get detailed farmer profile with relationships
        """
        farmer = Farmer.nodes.get_or_none(farmer_id=farmer_id)
        if not farmer:
            return None

        # Initialize lists for relationship data
        member_of = []
        located_in = None
        trained_by = []
        participated_in = []
        has_adopted = []
        receives = []

        # Fetch cooperatives (member_of)
        try:
            cooperatives = farmer.member_of.all()
            member_of = [coop.name for coop in cooperatives]
        except Exception:
            pass  # If there's an error, leave as empty list

        # Fetch ward (located_in)
        try:
            ward = farmer.located_in.single()
            if ward:
                # We can return just the name, or a string representation
                located_in = f"{ward.name} ({ward.code})" if ward.code else ward.name
        except Exception:
            pass  # If there's an error, leave as None

        # Fetch trainers (trained_by) - note: this is a RelationshipFrom, so we need to access the source
        try:
            trainers = farmer.trained_by.all()
            trained_by = [trainer.name for trainer in trainers]
        except Exception:
            pass

        # Fetch training sessions (participated_in)
        try:
            trainings = farmer.participated_in.all()
            participated_in = [getattr(training, 'title', str(training)) for training in trainings]
        except Exception:
            pass

        # Fetch input products (has_adopted)
        try:
            products = farmer.has_adopted.all()
            has_adopted = [product.name for product in products]
        except Exception:
            pass

        # Fetch advisory recommendations (receives)
        try:
            recommendations = farmer.receives.all()
            receives = [
                f"{rec.recommendation_type}: {rec.advice[:50]}..." if rec.advice and len(rec.advice) > 50
                else f"{rec.recommendation_type}: {rec.advice}"
                for rec in recommendations
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
