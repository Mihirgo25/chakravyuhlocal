from datetime import datetime
from pydantic import BaseModel

class CreateFclFreightRateStatisticsFromSelf(BaseModel):
    validity_id: str
    shipment_id: str
    shipment_fcl_freight_rate_services_id: str
    created_at: datetime
    updated_at: datetime
    

class CreateFclFreightRateStatisticsFromSpotSearch(BaseModel):
    validity_id: str
    spot_search_id: str
    spot_search_fcl_freight_rate_services_id: str
    created_at: datetime
    
    
class CreateFclFreightRateStatisticsFromCheckout(BaseModel):
    validity_id: str
    checkout_id: str
    checkout_fcl_freight_rate_services_id: str
    created_at: datetime
    
    
class CreateFclFreightRateStatisticsFromQuotation(BaseModel):
    validity_id: str
    quotation_id: str
    created_at: datetime
    updated_at: datetime
    

class CreateFclFreightRateStatisticsFromShipment(BaseModel):
    validity_id: str
    shipment_id: str
    shipment_fcl_freight_rate_services_id: str
    created_at: datetime
    updated_at: datetime