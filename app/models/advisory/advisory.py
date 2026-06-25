"""
Advisory Recommendation Model using Direct Neo4j Driver
"""
from app.database import get_db
from datetime import datetime

class AdvisoryRecommendation:
    """AdvisoryRecommendation node model using direct Neo4j driver"""

    LABEL = "AdvisoryRecommendation"

    def __init__(self, recommendation_type=None, advice=None, date_given=None,
                 valid_until=None, priority_score=0, confidence_score=0.0, uid=None):
        self.recommendation_type = recommendation_type
        self.advice = advice
        self.date_given = date_given or datetime.now()
        self.valid_until = valid_until
        self.priority_score = priority_score
        self.confidence_score = confidence_score
        self.uid = uid

    def save(self):
        """Save advisory recommendation node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (ar:AdvisoryRecommendation {uid: $uid})
        ON CREATE SET
            ar.recommendation_type = $recommendation_type,
            ar.advice = $advice,
            ar.date_given = $date_given,
            ar.valid_until = $valid_until,
            ar.priority_score = $priority_score,
            ar.confidence_score = $confidence_score
        ON MATCH SET
            ar.recommendation_type = $recommendation_type,
            ar.advice = $advice,
            ar.date_given = $date_given,
            ar.valid_until = $valid_until,
            ar.priority_score = $priority_score,
            ar.confidence_score = $confidence_score
        RETURN ar
        """
        parameters = {
            "recommendation_type": self.recommendation_type,
            "advice": self.advice,
            "date_given": self.date_given,
            "valid_until": self.valid_until,
            "priority_score": self.priority_score,
            "confidence_score": self.confidence_score,
            "uid": self.uid
        }

        result = db.execute_write(query, parameters)
        return result[0]["ar"] if result else None

    @classmethod
    def get_by_uid(cls, uid):
        """Get advisory recommendation by UID"""
        db = get_db()
        query = """
        MATCH (ar:AdvisoryRecommendation {uid: $uid})
        RETURN ar
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["ar"]
            return cls(
                recommendation_type=record["recommendation_type"],
                advice=record["advice"],
                date_given=record["date_given"],
                valid_until=record["valid_until"],
                priority_score=record["priority_score"],
                confidence_score=record["confidence_score"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all advisory recommendations"""
        db = get_db()
        query = """
        MATCH (ar:AdvisoryRecommendation)
        RETURN ar
        """
        result = db.execute_query(query)
        recommendations = []
        for record in result:
            record_data = record["ar"]
            recommendations.append(cls(
                recommendation_type=record_data["recommendation_type"],
                advice=record_data["advice"],
                date_given=record_data["date_given"],
                valid_until=record_data["valid_until"],
                priority_score=record_data["priority_score"],
                confidence_score=record_data["confidence_score"],
                uid=record_data["uid"]
            ))
        return recommendations

    def farmers(self):
        """Get relationship to farmers (recommended_for)"""
        db = get_db()
        query = """
        MATCH (ar:AdvisoryRecommendation {uid: $uid})-[:RECOMMENDED_FOR]->(f:Farmer)
        RETURN f
        """
        result = db.execute_query(query, {"uid": self.uid})
        from app.models.farmer import Farmer
        farmers = []
        for record in result:
            record_data = record["f"]
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

    def weather_stations(self):
        """Get relationship to weather stations (based_on_conditions)"""
        db = get_db()
        query = """
        MATCH (ar:AdvisoryRecommendation {uid: $uid})-[:BASED_ON_CONDITIONS]->(ws:WeatherStation)
        RETURN ws
        """
        result = db.execute_query(query, {"uid": self.uid})
        from app.models.weather.weather_station import WeatherStation
        stations = []
        for record in result:
            record_data = record["ws"]
            stations.append(WeatherStation(
                name=record_data["name"],
                location=record_data["location"],
                station_id=record_data["station_id"],
                uid=record_data["uid"]
            ))
        return stations

    def input_products(self):
        """Get relationship to input products (suggests_input)"""
        db = get_db()
        query = """
        MATCH (ar:AdvisoryRecommendation {uid: $uid})-[:SUGGESTS_INPUT]->(ip:InputProduct)
        RETURN ip
        """
        result = db.execute_query(query, {"uid": self.uid})
        from app.models.input_product.input_product import InputProduct
        products = []
        for record in result:
            record_data = record["ip"]
            products.append(InputProduct(
                name=record_data["name"],
                type_=record_data["type"],
                brand=record_data["brand"],
                cost=record_data["cost"],
                effectiveness_rating=record_data["effectiveness_rating"],
                uid=record_data["uid"]
            ))
        return products

    def receiving_farmers(self):
        """Get relationship to farmers (receives_recommendation)"""
        db = get_db()
        query = """
        MATCH (ar:AdvisoryRecommendation {uid: $uid})<-[:RECEIVES]-(f:Farmer)
        RETURN f
        """
        result = db.execute_query(query, {"uid": self.uid})
        from app.models.farmer import Farmer
        farmers = []
        for record in result:
            record_data = record["f"]
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