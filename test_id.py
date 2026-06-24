import os
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'password'
os.environ['NEO4J_DATABASE'] = 'neo4j'

from neomodel import db
# Set up a dummy connection? We'll just try to ignore connection errors for attribute access.
from app.models.farmer import Farmer
from app.schemas.farmer import FarmerResponse

# Create a farmer instance (not saved)
farmer = Farmer(farmer_id='DC00001', gender='Male', age_bracket='26-35', phone='+254700000000',
                registration_method='mobile_app', belongs_to_cooperative=False,
                herd_size=5, acres_under_cultivation=2.5, primary_enterprise='dairy')
print('Farmer instance created')
print('Farmer.farmer_id:', farmer.farmer_id)
print('Hasattr id?', hasattr(farmer, 'id'))
try:
    print('Farmer.id:', farmer.id)
except Exception as e:
    print('Error accessing farmer.id:', e)

# Now try to create FarmerResponse
try:
    response = FarmerResponse.from_orm(farmer)
    print('Success:', response)
except Exception as e:
    print('Error creating FarmerResponse:', e)
    import traceback
    traceback.print_exc()
