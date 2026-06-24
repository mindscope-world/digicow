from app.models.farmer import Farmer
from app.schemas.farmer import FarmerCreate

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
print('Farmer attributes:')
attrs = [attr for attr in dir(farmer) if not attr.startswith('_')]
print(attrs)
print()
print('Has element_id?', hasattr(farmer, 'element_id'))
if hasattr(farmer, 'element_id'):
    print('element_id:', farmer.element_id)
print('Has id?', hasattr(farmer, 'id'))
if hasattr(farmer, 'id'):
    try:
        print('id:', farmer.id)
    except Exception as e:
        print('Error getting id:', e)
print()
print('Farmer.farmer_id:', farmer.farmer_id)
