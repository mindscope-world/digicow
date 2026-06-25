from neomodel import db

query = "MATCH (n) DETACH DELETE n"
db.cypher_query(query)
print("Deleted all nodes and relationships.")