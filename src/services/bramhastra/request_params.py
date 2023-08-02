from datetime import datetime, date
from pydantic import BaseModel, validator, Field
from typing import Optional


class LineItems(BaseModel):
    price: str
    market_price: str
    currency: str
    unit: str
    code: str


class FclValidities(BaseModel):
    validity_id: str = Field(alias="id")
    last_action: str = Field(alias="action")
    price: float
    currency: str
    market_price: str
    validity_start: date
    validity_end: date
    line_items: list[LineItems]
    schedule_type: str
    payment_term: str
    likes_count: int
    dislikes_count: int


class FclFreight(BaseModel):
    rate_id: str = Field(alias="id")
    commodity: str
    container_size: str
    container_type: str
    containers_count: int
    destination_country_id: str = None
    destination_local_id: str = None
    destination_detention_id: str = None
    destination_demurrage_id: str = None
    destination_main_port_id: str = None
    destination_port_id: str
    destination_trade_id: str = None
    origin_country_id: str = None
    origin_local_id: str = None
    origin_detention_id: str = None
    origin_demurrage_id: str = None
    origin_main_port_id: str = None
    origin_port_id: str
    origin_trade_id: str = None
    service_provider_id: str
    shipping_line_id: str
    mode: str
    accuracy: float
    cogo_entity_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None
    rate_type: str
    validities: list[FclValidities]
    rate_created_at: datetime = Field(alias="created_at")
    rate_updated_at: datetime = Field(alias="updated_at")

    @validator("containers_count", pre=True)
    def convert_invalid_container_count(cls, v):
        if isinstance(cls, str) or not v:
            v = 1

        return v


class CreateFclFreightRateStatistic(BaseModel):
    freight: FclFreight


class UpdateFclFreightRateStatistic(BaseModel):
    pass


class ApplyFclFreightRateStatistic(BaseModel):
    action: str
    create_params: CreateFclFreightRateStatistic = None
    update_params: UpdateFclFreightRateStatistic = None


# Apply Spot Search Fcl Freight Statistics

class Rates(BaseModel):
    rate_id: str
    validity_id: str
    payment_term: str
    schedule_type: str = 'direct'
    
    @validator("payment_term", pre=True)
    def convert_invalid_payment_term(cls, v):
        if not v:
            v = "prepaid"
        return v
    
    @validator("schedule_type", pre=True)
    def convert_invalid_schedule_type(cls, v):
        if not v:
            v = "direct"
        return v


class SpotSearchFclFreightRateStatistic(BaseModel):
    spot_search_id: str
    spot_search_fcl_freight_services_id: str
    rates: list[Rates]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    

class ApplySpotSearchFclFreightRateStatistic(BaseModel):
    action: str
    params: SpotSearchFclFreightRateStatistic
    
    
# Apply Checkout Fcl Freight Statistics

class CheckoutRates(BaseModel):
    rate_id: str
    source: str
    validity_id: str
    line_items: list[dict]
    

class CheckoutFclFreightService(BaseModel):
    checkout_id: str
    checkout_fcl_freight_service_id: str = Field(alias='id')
    rate: CheckoutRates
    

class FclFreightCheckoutParams(BaseModel):
    source: str
    source_id: str
    importer_exporter_id: str
    created_at: datetime
    updated_at: datetime
    checkout_fcl_freight_services: list[CheckoutFclFreightService]


class ApplyCheckoutFclFreightRateStatistic(BaseModel):
    params: FclFreightCheckoutParams = None
    action: str
    
    
# Apply Feedback Fcl Freight Statistics

class FeedbackFclFreightRateStatistic(BaseModel):
    feedback_id: str = Field(alias='id')
    validity_id: str
    rate_id: str = Field(alias='fcl_freight_rate_id')
    feedback_type: str
    source: str
    source_id: str
    serial_id: str = None
    importer_exporter_id: str = None
    service_provider_id: str = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    performed_by_id: str
    performed_by_org_id: str
    closed_by_id: str = None
    likes_count: int
    dislikes_count: int

class ApplyFeedbackFclFreightRateStatistics(BaseModel):
    action: str
    params: FeedbackFclFreightRateStatistic = None


class ApplyQuotationFclFreightRateStatistics(BaseModel):
    pass


class ApplyShipmentFclFreightRateStatistics(BaseModel):
    pass


class WeightSlab(BaseModel):
    lower_limit: float
    upper_limit: float
    tariff_price: float
    currency: str
    unit: str = "per_kg"

class AirValidities(BaseModel):
    validity_start: date
    validity_end: date
    validity_id: str = Field(alias="id")
    last_action: str = Field(alias="action")
    currency: str
    status: bool = True
    likes_count: int = None
    dislikes_count: int = None
    weight_slabs: list[WeightSlab] = []
    density_category: str = 'general'
    min_density_weight: float = None
    max_density_weight: float = None


class AirFreight(BaseModel):
    rate_id: str = Field(alias="id")
    airline_id: str
    commodity: str
    commodity_type: str
    commodity_sub_type: str
    destination_airport_id: str = None
    destination_continent_id: str = None
    destination_country_id: str = None
    destination_local_id: str = None
    destination_trade_id: str = None
    operation_type: str = None
    origin_airport_id: str = None
    origin_continent_id: str = None
    origin_country_id: str = None
    origin_local_id: str = None
    origin_trade_id: str = None
    price_type: str = None
    rate_type: str
    service_provider_id: str
    shipment_type: str = None
    stacking_type: str = None
    surcharge_id: str = None
    validities: list[AirValidities]
    source: str
    accuracy: float
    cogo_entity_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None
    rate_created_at: datetime = Field(alias="created_at")
    rate_updated_at: datetime = Field(alias="updated_at")


class CreateAirFreightRateStatistic(BaseModel):
    freight: AirFreight


class UpdateAirFreightRateStatistic(BaseModel):
    pass


class ApplyAirFreightRateStatistic(BaseModel):
    action: str
    create_params: CreateAirFreightRateStatistic = None
    update_params: UpdateAirFreightRateStatistic = None



# Apply Feedback Air Freight Statistics

class FeedbackAirFreightRateStatistic(BaseModel):
    feedback_id: str = Field(alias='id')
    validity_id: str
    rate_id: str = Field(alias='air_freight_rate_id')
    feedback_type: str
    source: str
    source_id: str
    serial_id: str = None
    importer_exporter_id: str = None
    service_provider_id: str = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    performed_by_id: str
    performed_by_org_id: str
    closed_by_id: str = None
    likes_count: int
    dislikes_count: int

class ApplyFeedbackAirFreightRateStatistics(BaseModel):
    action: str
    params: FeedbackAirFreightRateStatistic = None