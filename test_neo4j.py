from neomodel import config, db
from app.core.config import settings

# Configure neomodel
config.DATABASE_URL = f"bolt://{settings.NEO4J_USER}:{settings.NEO4J_PASSWORD}@{settings.NEO4J_URI.replace('bolt://', '')}"
print(f"Connecting to: {config.DATABASE_URL}")

try:
    # Test the connection by running a simple query
    results, meta = db.cypher_query("RETURN 1 as test")
    print(f"Successfully connected to Neo4j! Result: {results[0][0]}")
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")
    print(f"Error type: {type(e)}")