from datetime import datetime, date
from pydantic import BaseModel, validator, Field, root_validator
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
    source: str
    source_id: str
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


class FclFreightRateStatistic(BaseModel):
    freight: FclFreight


class ApplyFclFreightRateStatistic(BaseModel):
    action: str
    params: FclFreightRateStatistic = None


# Apply Spot Search Fcl Freight Statistics


class Rates(BaseModel):
    rate_id: str
    validity_id: str
    payment_term: str
    schedule_type: str = "direct"

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
    checkout_fcl_freight_service_id: str = Field(alias="id")
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
    feedback_id: str = Field(alias="id")
    validity_id: str = None
    rate_id: str = Field(alias="fcl_freight_rate_id", default=None)
    feedback_type: str = None
    source: str = None
    source_id: str = None
    serial_id: str = None
    importer_exporter_id: str = None
    service_provider_id: str = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    performed_by_id: str = None
    performed_by_org_id: str = None
    closed_by_id: str = None
    likes_count: int = None
    dislikes_count: int = None
    status: str = "active"


class ApplyFeedbackFclFreightRateStatistics(BaseModel):
    action: str
    params: FeedbackFclFreightRateStatistic


class FclFreightServices(BaseModel):
    shipment_fcl_freight_service_id: str = Field(alias="id")
    shipment_id: str
    service_state: str = Field(alias='state')
    service_is_active: bool = Field(alias='is_active')
    service_cancellation_reason: str = Field(alias='cancellation_reason')
    service_created_at: datetime = Field(alias='created_at',default=datetime.utcnow())
    service_updated_at: datetime = Field(alias='updated_at',default=datetime.utcnow())
    shipping_line_id: str
    service_provider_id: str


class SellQuotation(BaseModel):
    sell_quotation_id: str = Field(alias="id")
    service_id: str = None
    service_type: str = None
    total_price: float
    total_price_discounted: float
    tax_price: float
    tax_price_discounted: float
    tax_total_price: float
    tax_total_price_discounted: float
    currency: str
    is_deleted: bool
    sell_quotation_created_at: datetime = Field(alias='created_at',default=datetime.utcnow())
    sell_quotation_updated_at: datetime = Field(alias='updated_at',default=datetime.utcnow())


class Shipment(BaseModel):
    shipment_id: str = Field(alias="id")
    serial_id: int
    importer_exporter_id: str = None
    shipment_type: str
    services: list[str]
    source: str = None
    source_id: str = None
    state: str
    created_at: datetime
    updated_at: datetime
    cancellation_reason: str = None


class ShipmentParams(BaseModel):
    fcl_freight_services: list[FclFreightServices]
    sell_quotations: list[SellQuotation]
    shipment: Shipment


class ApplyShipmentFclFreightRateStatistics(BaseModel):
    action: str
    params: ShipmentParams


class FclFreightRateRequest(BaseModel):
    rate_request_id: str = Field(alias="id", default=None)
    origin_port_id: str = None
    destination_port_id: str = None
    origin_region_id: str = None
    destination_region_id: str = None
    origin_country_id: str = None
    destination_country_id: str = None
    origin_continent_id: str = None
    destination_continent_id: str = None
    origin_trade_id: str = None
    destination_trade_id: str = None
    origin_pricing_zone_map_id: str = None
    destination_pricing_zone_map_id: str = None
    request_type: str = None
    serial_id: str = None
    source: str = None
    source_id: str = None
    performed_by_id: str = None
    performed_by_org_id: str = None
    importer_exporter_id: str = None
    closing_remarks: list[str] = None
    closed_by_id: str = None
    container_size: str = None
    commodity: str = None
    containers_count: int
    is_rate_reverted: bool = None
    created_at: datetime = None
    updated_at: datetime = None
    status: str = None

    @validator("closing_remarks", always=True)
    def add_is_rate_reverted(cls, value, values):
        values["is_rate_reverted"] = True if "rate_added" in value else False
        return values


class ApplyFclFreightRateRequestStatistic(BaseModel):
    action: str
    params: FclFreightRateRequest


######## AIR ##########


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
    density_category: str = "general"
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
    feedback_id: str = Field(alias="id")
    validity_id: str = None
    rate_id: str = Field(alias="air_freight_rate_id")
    feedback_type: str = None
    source: str = None
    source_id: str = None
    serial_id: str = None
    importer_exporter_id: str = None
    service_provider_id: str = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    performed_by_id: str = None
    performed_by_org_id: str = None
    closed_by_id: str = None
    likes_count: int = None
    dislikes_count: int = None


class ApplyFeedbackAirFreightRateStatistics(BaseModel):
    action: str
    params: FeedbackAirFreightRateStatistic = None
