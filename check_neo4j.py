from app.database import get_db
db = get_db()
labels, _ = db.cypher_query("CALL db.labels()")
print("Labels:")
for row in labels:
    print(row[0])
rels, _ = db.cypher_query("CALL db.relationshipTypes()")
print("\nRelationship types:")
for row in rels:
    print(row[0])
# Also check for Farmer and Ward nodes count
f_count, _ = db.cypher_query("MATCH (f:Farmer) RETURN count(f) as cnt")
print("\nFarmer count:", f_count[0][0])
w_count, _ = db.cypher_query("MATCH (w:Ward) RETURN count(w) as cnt")
print("Ward count:", w_count[0][0])
# Check LOCATED_IN rel count
li_count, _ = db.cypher_query("MATCH (f:Farmer)-[:LOCATED_IN]->(w:Ward) RETURN count(*) as cnt")
print("LOCATED_IN relationships:", li_count[0][0])