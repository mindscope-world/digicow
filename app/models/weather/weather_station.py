"""
Weather Station Model using Direct Neo4j Driver
"""
from app.database import get_db
from datetime import datetime

class WeatherStation:
    """WeatherStation node model using direct Neo4j driver"""

    LABEL = "WeatherStation"

    def __init__(self, station_id=None, name=None, location=None,
                 last_updated=None, uid=None):
        self.station_id = station_id
        self.name = name
        self.location = location
        self.last_updated = last_updated or datetime.now()
        self.uid = uid

    def save(self):
        """Save weather station node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (ws:WeatherStation {station_id: $station_id})
        ON CREATE SET
            ws.uid = $uid,
            ws.name = $name,
            ws.location = $location,
            ws.last_updated = $last_updated
        ON MATCH SET
            ws.name = $name,
            ws.location = $location,
            ws.last_updated = $last_updated
        RETURN ws
        """
        parameters = {
            "station_id": self.station_id,
            "name": self.name,
            "location": self.location,
            "last_updated": self.last_updated,
            "uid": self.uid
        }

        result = db.execute_write(query, parameters)
        return result[0]["ws"] if result else None

    @classmethod
    def get_by_station_id(cls, station_id):
        """Get weather station by station_id"""
        db = get_db()
        query = """
        MATCH (ws:WeatherStation {station_id: $station_id})
        RETURN ws
        """
        result = db.execute_query(query, {"station_id": station_id})
        if result:
            record = result[0]["ws"]
            return cls(
                station_id=record["station_id"],
                name=record["name"],
                location=record["location"],
                last_updated=record["last_updated"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_uid(cls, uid):
        """Get weather station by UID"""
        db = get_db()
        query = """
        MATCH (ws:WeatherStation {uid: $uid})
        RETURN ws
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["ws"]
            return cls(
                station_id=record["station_id"],
                name=record["name"],
                location=record["location"],
                last_updated=record["last_updated"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all weather stations"""
        db = get_db()
        query = """
        MATCH (ws:WeatherStation)
        RETURN ws
        """
        result = db.execute_query(query)
        stations = []
        for record in result:
            record_data = record["ws"]
            stations.append(cls(
                station_id=record_data["station_id"],
                name=record_data["name"],
                location=record_data["location"],
                last_updated=record_data["last_updated"],
                uid=record_data["uid"]
            ))
        return stations

    def wards(self):
        """Get relationship to wards (monitors)"""
        db = get_db()
        query = """
        MATCH (ws:WeatherStation {station_id: $station_id})-[:MONITORS]->(w:Ward)
        RETURN w
        """
        result = db.execute_query(query, {"station_id": self.station_id})
        from app.models.location.ward import Ward
        wards = []
        for record in result:
            record_data = record["w"]
            wards.append(Ward(
                name=record_data["name"],
                code=record_data["code"],
                uid=record_data["uid"]
            ))
        return wards

    def recommendations(self):
        """Get relationship to advisory recommendations (based_on_conditions)"""
        db = get_db()
        query = """
        MATCH (ws:WeatherStation {station_id: $station_id})<-[:BASED_ON_CONDITIONS]-(ar:AdvisoryRecommendation)
        RETURN ar
        """
        result = db.execute_query(query, {"station_id": self.station_id})
        from app.models.advisory.advisory import AdvisoryRecommendation
        recommendations = []
        for record in result:
            record_data = record["ar"]
            recommendations.append(AdvisoryRecommendation(
                recommendation_type=record_data["recommendation_type"],
                advice=record_data["advice"],
                date_given=record_data["date_given"],
                valid_until=record_data["valid_until"],
                priority_score=record_data["priority_score"],
                confidence_score=record_data["confidence_score"],
                uid=record_data["uid"]
            ))
        return recommendations