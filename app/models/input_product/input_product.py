"""
Input Product Model using Direct Neo4j Driver
"""
from app.database import get_db

class InputProduct:
    """InputProduct node model using direct Neo4j driver"""

    LABEL = "InputProduct"

    def __init__(self, name=None, type_="unknown", brand="unknown", cost="0",
                 effectiveness_rating=0, uid=None):
        self.name = name
        self.type = type_
        self.brand = brand
        self.cost = cost
        self.effectiveness_rating = effectiveness_rating
        self.uid = uid

    def save(self):
        """Save input product node to database"""
        db = get_db()
        if not self.uid:
            # Generate UID if not provided
            import uuid
            self.uid = str(uuid.uuid4())

        query = """
        MERGE (ip:InputProduct {name: $name})
        ON CREATE SET
            ip.uid = $uid,
            ip.type = $type,
            ip.brand = $brand,
            ip.cost = $cost,
            ip.effectiveness_rating = $effectiveness_rating
        ON MATCH SET
            ip.type = $type,
            ip.brand = $brand,
            ip.cost = $cost,
            ip.effectiveness_rating = $effectiveness_rating
        RETURN ip
        """
        parameters = {
            "name": self.name,
            "type": self.type,
            "brand": self.brand,
            "cost": self.cost,
            "effectiveness_rating": self.effectiveness_rating,
            "uid": self.uid
        }

        result = db.execute_write(query, parameters)
        return result[0]["ip"] if result else None

    @classmethod
    def get_by_name(cls, name):
        """Get input product by name"""
        db = get_db()
        query = """
        MATCH (ip:InputProduct {name: $name})
        RETURN ip
        """
        result = db.execute_query(query, {"name": name})
        if result:
            record = result[0]["ip"]
            return cls(
                name=record["name"],
                type=record["type"],
                brand=record["brand"],
                cost=record["cost"],
                effectiveness_rating=record["effectiveness_rating"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def get_by_uid(cls, uid):
        """Get input product by UID"""
        db = get_db()
        query = """
        MATCH (ip:InputProduct {uid: $uid})
        RETURN ip
        """
        result = db.execute_query(query, {"uid": uid})
        if result:
            record = result[0]["ip"]
            return cls(
                name=record["name"],
                type_=record["type"],
                brand=record["brand"],
                cost=record["cost"],
                effectiveness_rating=record["effectiveness_rating"],
                uid=record["uid"]
            )
        return None

    @classmethod
    def all(cls):
        """Get all input products"""
        db = get_db()
        query = """
        MATCH (ip:InputProduct)
        RETURN ip
        """
        result = db.execute_query(query)
        products = []
        for record in result:
            record_data = record["ip"]
            products.append(cls(
                name=record_data["name"],
                type_=record_data["type"],
                brand=record_data["brand"],
                cost=record_data["cost"],
                effectiveness_rating=record_data["effectiveness_rating"],
                uid=record_data["uid"]
            ))
        return products

    def topics(self):
        """Get relationship to training topics (SUITABLE_FOR_TOPIC)"""
        db = get_db()
        query = """
        MATCH (ip:InputProduct {name: $name})-[:SUITABLE_FOR_TOPIC]->(topic:TrainingTopic)
        RETURN topic
        """
        result = db.execute_query(query, {"name": self.name})
        from app.models.training.training_topic import TrainingTopic
        topics = []
        for record in result:
            record_data = record["topic"]
            topics.append(TrainingTopic(
                name=record_data["name"],
                category=record_data["category"],
                description=record_data["description"],
                uid=record_data["uid"]
            ))
        return topics

    def trainers(self):
        """Get relationship to trainers (PROMOTED_BY)"""
        db = get_db()
        query = """
        MATCH (ip:InputProduct {name: $name})-[:PROMOTED_BY]->(trainer:Trainer)
        RETURN trainer
        """
        result = db.execute_query(query, {"name": self.name})
        from app.models.trainer.trainer import Trainer
        trainers = []
        for record in result:
            record_data = record["trainer"]
            trainers.append(Trainer(
                name=record_data["name"],
                specialty_areas=record_data["specialty_areas"],
                contact_info=record_data["contact_info"],
                employee_id=record_data["employee_id"],
                uid=record_data["uid"]
            ))
        return trainers

    def adoptions(self):
        """Get relationship to adoptions (IS_ADOPTED_BY)"""
        db = get_db()
        query = """
        MATCH (ip:InputProduct {name: $name})<-[:IS_ADOPTED_BY]-(adoption:Adoption)
        RETURN adoption
        """
        result = db.execute_query(query, {"name": self.name})
        from app.models.adoption import Adoption
        adoptions = []
        for record in result:
            record_data = record["adoption"]
            adoptions.append(Adoption(
                uid=record_data["uid"],
                date_adopted=record_data["date_adopted"]
            ))
        return adoptions