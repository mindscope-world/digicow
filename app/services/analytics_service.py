"""Analytics Service Layer"""
from collections import defaultdict
from app.models.farmer import Farmer
from app.models.input_product.input_product import InputProduct
from app.models.adoption import Adoption
from app.models.training.TrainingSession import TrainingSession
from app.models.trainer.Trainer import Trainer
from app.models.location.ward import Ward
from datetime import datetime, timedelta


class AnalyticsService:
    """
    Service for computing analytics and reports
    """

    @staticmethod
    async def get_adoption_rates() -> list:
        """
        Get adoption rates by product
        Returns list of dicts with product, adoption_count, unique_farmers, adoption_rate (%)
        """
        # Get all adoptions
        adoptions = Adoption.nodes.all()
        product_stats = defaultdict(lambda: {"adoptions": 0, "farmers": set()})
        for adoption in adoptions:
            # Get product
            product = adoption.input_product.single()
            if not product:
                continue
            product_name = product.name
            # Get farmer
            farmer = adoption.farmer.single()
            if not farmer:
                continue
            product_stats[product_name]["adoptions"] += 1
            product_stats[product_name]["farmers"].add(farmer.farmer_id)
        result = []
        total_farmers = Farmer.nodes.count()
        for product_name, stats in product_stats.items():
            adoption_count = stats["adoptions"]
            unique_farmers = len(stats["farmers"])
            adoption_rate = (adoption_count / total_farmers * 100) if total_farmers > 0 else 0
            result.append({
                "product": product_name,
                "adoption_count": adoption_count,
                "unique_farmers": unique_farmers,
                "adoption_rate": round(adoption_rate, 2)
            })
        # Sort by adoption_count descending
        result.sort(key=lambda x: x["adoption_count"], reverse=True)
        return result

    @staticmethod
    async def get_trainer_effectiveness() -> list:
        """
        Get trainer performance metrics
        Returns list of dicts with trainer info, trainings conducted, total attendees, unique attendees
        """
        trainers = Trainer.nodes.all()
        # Get all training sessions
        trainings = TrainingSession.nodes.all()
        # Map training to trainer
        training_by_trainer = defaultdict(list)
        for training in trainings:
            trainer = training.conducted_by.single()
            if trainer:
                training_by_trainer[trainer].append(training)
        result = []
        for trainer in trainers:
            trainings_list = training_by_trainer.get(trainer, [])
            total_attendees = 0
            unique_attendees = set()
            for training in trainings_list:
                # Get farmers who participated in this training
                participants = training.participated_in.all()
                for participant in participants:
                    farmer = participant  # Participated_in is RelationshipFrom(Farmer, ...), so iterating gives Farmer nodes
                    total_attendees += 1
                    unique_attendees.add(farmer.farmer_id)
            result.append({
                "trainer_id": trainer.trainer_id,
                "trainer_name": trainer.name,
                "trainings_conducted": len(trainings_list),
                "total_attendees": total_attendees,
                "unique_attendees": len(unique_attendees),
                "average_attendance_per_training": round(total_attendees / len(trainings_list), 2) if trainings_list else 0
            })
        # Sort by trainings conducted descending
        result.sort(key=lambda x: x["trainings_conducted"], reverse=True)
        return result

    @staticmethod
    async def get_ward_performance() -> list:
        """
        Get performance metrics by ward
        Returns list of dicts with ward info, farmer count, adoption count, training attendance count
        """
        wards = Ward.nodes.all()
        # Precompute maps for efficiency
        farmer_ward_map = {}  # farmer_id -> ward_code
        for farmer in Farmer.nodes.all():
            ward = farmer.located_in.single()
            if ward:
                farmer_ward_map[farmer.farmer_id] = ward.code
        # Adoption counts per ward
        adoption_count_by_ward = defaultdict(int)
        for adoption in Adoption.nodes.all():
            farmer = adoption.farmer.single()
            if farmer and farmer.farmer_id in farmer_ward_map:
                ward_code = farmer_ward_map[farmer.farmer_id]
                adoption_count_by_ward[ward_code] += 1
        # Training attendance per ward
        training_count_by_ward = defaultdict(int)
        for training in TrainingSession.nodes.all():
            participants = training.participated_in.all()
            for participant in participants:
                farmer = participant
                if farmer.farmer_id in farmer_ward_map:
                    ward_code = farmer_ward_map[farmer.farmer_id]
                    training_count_by_ward[ward_code] += 1
        result = []
        for ward in wards:
            ward_code = ward.code
            # Count farmers in this ward
            farmer_count = sum(1 for fid in farmer_ward_map.values() if fid == ward_code)
            result.append({
                "ward_code": ward_code,
                "ward_name": ward.name,
                "farmer_count": farmer_count,
                "adoption_count": adoption_count_by_ward.get(ward_code, 0),
                "training_attendance_count": training_count_by_ward.get(ward_code, 0),
                "adoption_rate": round((adoption_count_by_ward.get(ward_code, 0) / farmer_count * 100), 2) if farmer_count > 0 else 0
            })
        # Sort by adoption_count descending
        result.sort(key=lambda x: x["adoption_count"], reverse=True)
        return result

    @staticmethod
    async def get_trends() -> dict:
        """
        Get temporal trends in adoption and training (last 6 months)
        Returns dict with monthly counts for adoptions and trainings
        """
        # Determine months
        today = datetime.today()
        months = []
        for i in range(5, -1, -1):  # last 6 months including current
            month = today.replace(day=1) - timedelta(days=30*i)
            months.append(month.strftime("%Y-%m"))
        # Initialize counters
        adoption_counts = {month: 0 for month in months}
        training_counts = {month: 0 for month in months}
        # Count adoptions per month
        for adoption in Adoption.nodes.all():
            dt = adoption.date_adopted
            month_key = dt.strftime("%Y-%m")
            if month_key in adoption_counts:
                adoption_counts[month_key] += 1
        # Count trainings per month
        for training in TrainingSession.nodes.all():
            dt = training.session_date
            month_key = dt.strftime("%Y-%m")
            if month_key in training_counts:
                training_counts[month_key] += 1
        # Format as list of dicts for charting
        adoption_trend = [{"month": m, "count": adoption_counts[m]} for m in months]
        training_trend = [{"month": m, "count": training_counts[m]} for m in months]
        return {
            "adoption_trend": adoption_trend,
            "training_trend": training_trend
        }


# Instantiate
analytics_service = AnalyticsService()