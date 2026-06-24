import os
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'password'
os.environ['NEO4J_DATABASE'] = 'neo4j'

from app.models.farmer import Farmer
from app.schemas.farmer import FarmerCreate, FarmerResponse

# Create a farmer instance (not saved)
data = FarmerCreate(
    farmer_id='DC00001',
    gender='Male',
    age_bracket='26-35',
    phone='+254700000000',
    registration_method='mobile_app',
    belongs_to_cooperative=False,
    herd_size=5,
    acres_under_cultivation=2.5,
    primary_enterprise='dairy'
)
farmer = Farmer(**data.dict())
print('Farmer created')
print('farmer.farmer_id:', farmer.farmer_id)

# Try to create FarmerResponse
try:
    # Using from_orm (deprecated but should work)
    response = FarmerResponse.from_orm(farmer)
    print('Success! FarmerResponse:')
    print('  id:', response.id)
    print('  farmer_id:', response.farmer_id)
    print('  gender:', response.gender)
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()

# Also test with model_validate (v2) if available
try:
    response2 = FarmerResponse.model_validate(farmer)
    print('Using model_validate also works:')
    print('  id:', response2.id)
except Exception as e:
    print('model_validate error:', e)
