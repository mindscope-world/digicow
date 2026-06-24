"""
Database Utilities
"""
from neomodel import config, db
from app.core.config import settings


def init_neo4j():
    """
    Initialize Neo4j connection
    """
    config.DATABASE_URL = settings.NEO4J_URI
    # In a real implementation, we would also set up credentials
    # For now, we'll assume the database is running with default credentials
    
    # Test connection
    try:
        db.cypher_query("RETURN 1")
        print("Connected to Neo4j successfully")
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")


def get_db():
    """
    Get database connection
    """
    return db
