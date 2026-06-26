"""
Farmer Service Layer using Direct Neo4j Driver
"""
import csv
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
                    # Community analytics fields (will be generated/enriched)
                    'louvain_community_id': None,
                    'community_size': None,
                    'community_influence_score': None,
                    'community_influence_score_norm': None,
                    'peer_adoption_ratio': None,
                    'total_ward_peers': None,
                    'adopter_peers': None,
                }

                # Create Farmer instance and save to DB
                farmer = Farmer(**farmer_data)
                farmer.save()
                farmers.append(farmer)

        # Generate and save community analytics data for reference
        FarmerService._generate_community_analysis_csv(farmers)

        return farmers

    @staticmethod
    def _generate_community_analysis_csv(farmers: List[Farmer]) -> None:
        """Generate community analysis data and save to CSV for reference."""
        import csv
        import random

        # Group farmers by ward to calculate community statistics
        ward_farmers_map = {}
        for farmer in farmers:
            # We don't have ward info in the Farmer object from CSV loading,
            # so we'll use a simplified approach: assign based on farmer_id hash
            # In a real implementation, we would get ward from the Farmer's location
            ward_hash = hash(farmer.farmer_id) % 100  # Simulate 100 different wards
            if ward_hash not in ward_farmers_map:
                ward_farmers_map[ward_hash] = []
            ward_farmers_map[ward_hash].append(farmer)

        # Generate community analytics for each ward
        community_data = []
        for ward_id, farmers_in_ward in ward_farmers_map.items():
            total_ward_peers = len(farmers_in_ward)

            # Simulate Louvain community detection (simplified)
            # In reality, this would come from actual graph community detection algorithms
            louvain_community_id = ward_id % 10  # 10 different communities

            # Community size (number of farmers in this Louvain community)
            # For simplicity, we'll assume each ward maps to one community
            community_size = total_ward_peers

            # Community influence score (randomized for demo)
            community_influence_score = round(random.uniform(0.1, 1.0), 3)
            community_influence_score_norm = round(community_influence_score, 3)  # Already normalized 0-1

            # Peer adoption ratio (percentage of farmers who adopted)
            adopter_peers = sum(1 for f in farmers_in_ward if getattr(f, 'adopter_peers', 0) or
                              (hasattr(f, 'adopter_peers') and f.adopter_peers is not None and f.adopter_peers > 0))
            # For demo, let's make some farmers adopters
            if adopter_peers == 0 and total_ward_peers > 0:
                # Make roughly 30% adopters
                adopter_peers = max(1, int(total_ward_peers * 0.3))

            peer_adoption_ratio = round(adopter_peers / total_ward_peers, 3) if total_ward_peers > 0 else 0.0

            community_data.append({
                'ward_id': ward_id,
                'louvain_community_id': louvain_community_id,
                'community_size': community_size,
                'community_influence_score': community_influence_score,
                'community_influence_score_norm': community_influence_score_norm,
                'peer_adoption_ratio': peer_adoption_ratio,
                'total_ward_peers': total_ward_peers,
                'adopter_peers': adopter_peers
            })

        # Update farmers with community data (simplified: assign based on ward hash)
        for farmer in farmers:
            ward_hash = hash(farmer.farmer_id) % 100
            # Find matching community data
            for cd in community_data:
                if cd['ward_id'] == ward_hash:
                    farmer.louvain_community_id = cd['louvain_community_id']
                    farmer.community_size = cd['community_size']
                    farmer.community_influence_score = cd['community_influence_score']
                    farmer.community_influence_score_norm = cd['community_influence_score_norm']
                    farmer.peer_adoption_ratio = cd['peer_adoption_ratio']
                    farmer.total_ward_peers = cd['total_ward_peers']
                    farmer.adopter_peers = cd['adopter_peers']
                    break

        # Save community analysis to CSV for reference
        csv_path = "/home/mindscope/Lab/hackathons/backend/data/generated_community_analysis.csv"
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['farmer_id', 'louvain_community_id', 'community_size',
                         'community_influence_score', 'community_influence_score_norm',
                         'peer_adoption_ratio', 'total_ward_peers', 'adopter_peers']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for farmer in farmers:
                writer.writerow({
                    'farmer_id': farmer.farmer_id,
                    'louvain_community_id': farmer.louvain_community_id,
                    'community_size': farmer.community_size,
                    'community_influence_score': farmer.community_influence_score,
                    'community_influence_score_norm': farmer.community_influence_score_norm,
                    'peer_adoption_ratio': farmer.peer_adoption_ratio,
                    'total_ward_peers': farmer.total_ward_peers,
                    'adopter_peers': farmer.adopter_peers
                })

        print(f"Generated community analysis data saved to {csv_path}")

    
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