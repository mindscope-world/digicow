from app.models.farmer import Farmer

farmers = Farmer.nodes.filter(farmer_id='DC00001')
print(f"Found {len(farmers)} farmers with ID DC00001")
for f in farmers:
    print(f"  - {f}")