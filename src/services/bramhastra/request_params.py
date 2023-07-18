from datetime import datetime, date
from pydantic import BaseModel, validator, Field


# Apply Fcl Freight Statistics


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

class CreateCheckoutFclFreightRateStatistic(BaseModel):
    pass


class UpdateCheckoutFclFreightRateStatistic(BaseModel):
    pass


class CreateQuotationFclFreightRateStatistic(BaseModel):
    pass


class UpdateQuotationFclFreightRateStatistic(BaseModel):
    pass


class CreateShipmentFclFreightRateStatistic(BaseModel):
    pass


class UpdateShipmentFclFreightRateStatistic(BaseModel):
    pass


class CreateFeedbackFclFreightRateStatistic(BaseModel):
    pass


class UpdateFeedbackFclFreightRateStatistic(BaseModel):
    pass


class ApplyCheckoutFclFreightRateStatistic(BaseModel):
    create_params: CreateCheckoutFclFreightRateStatistic = None
    update_params: UpdateCheckoutFclFreightRateStatistic = None


class ApplyQuotationFclFreightRateStatistics(BaseModel):
    create_params: CreateQuotationFclFreightRateStatistic = None
    update_params: UpdateQuotationFclFreightRateStatistic = None


class ApplyShipmentFclFreightRateStatistics(BaseModel):
    create_params: CreateShipmentFclFreightRateStatistic = None
    update_params: UpdateShipmentFclFreightRateStatistic = None


class ApplyFeedbackFclFreightRateStatistics(BaseModel):
    create_params: CreateFeedbackFclFreightRateStatistic = None
    update_params: UpdateFeedbackFclFreightRateStatistic = None
