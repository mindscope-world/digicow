"""
Neo4j Database Connection Module
"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Neo4jConnection:
    """Handles connection to Neo4j database"""

    def __init__(self, uri=None, user=None, password=None):
        """
        Initialize Neo4j connection

        Args:
            uri (str): Neo4j URI (default from env)
            user (str): Username (default from env)
            password (str): Password (default from env)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None

    def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Verify connection
            self.driver.verify_connectivity()
            print("Successfully connected to Neo4j")
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            return False

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()

    def execute_query(self, query, parameters=None):
        """
        Execute a Cypher query

        Args:
            query (str): Cypher query to execute
            parameters (dict): Query parameters

        Returns:
            list: Query results
        """
        if not self.driver:
            raise Exception("Not connected to Neo4j")

        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

    def execute_write(self, query, parameters=None):
        """
        Execute a write Cypher query

        Args:
            query (str): Cypher query to execute
            parameters (dict): Query parameters

        Returns:
            list: Query results
        """
        if not self.driver:
            raise Exception("Not connected to Neo4j")

        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

# Global connection instance
db_connection = Neo4jConnection()

# Initialize connection when module is imported
try:
    db_connection.connect()
    print("Connected to Neo4j successfully")
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")

def get_db():
    """Get database connection instance"""
    return db_connection