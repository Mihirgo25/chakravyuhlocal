from pydantic import BaseModel
    
class CreateFuelData(BaseModel):
    location_id: str 
    location_type: str
    fuel_type: str
    fuel_price: float
    fuel_unit: str
    currency:str
    