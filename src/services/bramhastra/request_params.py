from datetime import datetime, date
from pydantic import BaseModel, validator, Field


class LineItems(BaseModel):
    price: str
    market_price: str
    currency: str
    unit: str
    code: str


class FclValidities(BaseModel):
    validity_id: str = Field(alias="id")
    last_action: str = Field(alias="action", default = "create")
    price: float
    currency: str
    market_price: str
    validity_start: date
    validity_end: date
    line_items: list[LineItems] = []
    schedule_type: str = "direct"
    payment_term: str = "prepaid"
    likes_count: int = 0
    dislikes_count: int = 0


class FclFreight(BaseModel):
    rate_id: str = Field(alias="id")
    commodity: str
    container_size: str
    container_type: str
    containers_count: int
    destination_country_id: str = None
    destination_local_id: str = None
    destination_detention_id: str = None
    origin_region_id: str = None
    destination_region_id: str = None
    origin_continent_id: str = None
    destination_continent_id: str = None
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
    source: str = None
    source_id: str = None
    cogo_entity_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None
    rate_type: str
    validities: list[FclValidities]
    rate_created_at: datetime = Field(alias="created_at")
    rate_updated_at: datetime = Field(alias="updated_at")
    updated_at: datetime
    created_at: datetime
    performed_by_id: str = None
    performed_by_type: str = None

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


class Rate(BaseModel):
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
    spot_search_id: str = None
    spot_search_fcl_freight_service_id: str = None
    rates: list[Rate] = []
    updated_at: datetime
    created_at: datetime
    origin_port_id: str
    origin_main_port_id: str = None
    origin_country_id: str = None
    origin_trade_id: str = None
    origin_continent_id: str = None
    destination_port_id: str
    destination_main_port_id: str = None
    destination_country_id: str = None
    destination_trade_id: str = None
    destination_continent_id: str = None
    container_size: str
    container_type: str
    commodity: str
    containers_count: int
    importer_exporter_id: str


class ApplySpotSearchFclFreightRateStatistic(BaseModel):
    action: str
    params: SpotSearchFclFreightRateStatistic


# Apply Checkout Fcl Freight Statistics


class CheckoutRate(BaseModel):
    rate_id: str
    source: str
    validity_id: str
    line_items: list[dict]


class CheckoutFclFreightService(BaseModel):
    checkout_id: str
    checkout_fcl_freight_service_id: str = Field(alias="id")
    rate: CheckoutRate


class FclFreightCheckoutParams(BaseModel):
    checkout_source: str = Field(alias="source")
    checkout_source_id: str = Field(alias="source_id")
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
    serial_id: int = 0
    preferred_freight_rate: float = None
    currency: str = Field(alias="preferred_freight_rate_currency", default="USD")
    importer_exporter_id: str = None
    service_provider_id: str = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    performed_by_id: str = None
    performed_by_org_id: str = None
    closed_by_id: str = None
    likes_count: int = None
    dislikes_count: int = None
    closing_remarks: list[str] = None
    is_rate_reverted: bool = None
    status: str = "active"

    @validator("preferred_freight_rate", pre=True)
    def convert_preferred_freight_rate(cls, v):
        if not v:
            v = 0
        return v
    
    @validator("serial_id", pre=True)
    def convert_serial_id(cls, v):
        if not v:
            v = 0
        return v

    @validator("currency", pre=True)
    def convert_currency(cls, v):
        if not v:
            v = "USD"
        return v

    @validator("is_rate_reverted", always=True)
    def add_is_rate_reverted(cls, value, values):
        if values.get("closing_remarks"):
            closing_remarks = values.get("closing_remarks", [])
            return value or "rate_added" in closing_remarks
        return False

class ApplyFeedbackFclFreightRateStatistics(BaseModel):
    action: str
    params: FeedbackFclFreightRateStatistic


class BuyQuotation(BaseModel):
    buy_quotation_id: str = Field(alias="id")
    service_id: str = None
    service_type: str = None
    total_price: float = None
    total_price_discounted: float = None
    tax_price: float = None
    tax_price_discounted: float = None
    tax_total_price: float = None
    tax_total_price_discounted: float = None
    currency: str = None
    is_deleted: bool = None
    buy_quotation_created_at: datetime = Field(
        alias="created_at", default=datetime.utcnow()
    )
    buy_quotation_updated_at: datetime = Field(
        alias="updated_at", default=datetime.utcnow()
    )


class ShipmentFclFreightService(BaseModel):
    shipment_service_id: str = Field(alias="id")
    shipment_service_state: str = Field(alias="state", default=None)
    shipment_service_is_active: bool = Field(alias="is_active", default=None)
    shipment_service_cancellation_reason: str = Field(
        alias="cancellation_reason", default=None
    )
    shipment_service_created_at: datetime = Field(alias="created_at", default=None)
    shipment_service_updated_at: datetime = Field(
        alias="updated_at", default=datetime.utcnow()
    )
    shipping_line_id: str = None
    service_provider_id: str = None
    containers_count: int = None
    cargo_weight_per_container: float = None
    container_size: str = None
    container_type: str = None
    commodity: str = None


class Shipment(BaseModel):
    shipment_id: str = Field(alias="id")
    shipment_state: str = Field(alias="state", default=None)
    importer_exporter_id: str = None
    shipment_type: str = None
    services: list[str] = None
    shipment_source: str = Field(alias="source", default=None)
    shipment_source_id: str = Field(alias="source_id", default=None)
    shipment_created_at: datetime = Field(alias="created_at", default=None)
    shipment_updated_at: datetime = Field(alias="updated_at")


class FclShipmentParams(BaseModel):
    fcl_freight_services: list[ShipmentFclFreightService] = []
    shipment: Shipment
    checkout_id: str = None


class ApplyShipmentFclFreightRateStatistics(BaseModel):
    action: str
    params: FclShipmentParams = None
    shipment_update_params: Shipment = None
    shipment_service_update_params: ShipmentFclFreightService = None


class FclQuotationParams(BaseModel):
    fcl_freight_service: ShipmentFclFreightService = None
    buy_quotation: BuyQuotation = None
    shipment: Shipment = None


class ApplyQuotationFclFreightRateStatistics(BaseModel):
    params: list[FclQuotationParams]


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
    containers_count: int = 0
    is_rate_reverted: bool = None
    created_at: datetime = None
    updated_at: datetime = None
    status: str = None

    @validator("is_rate_reverted", always=True)
    def add_is_rate_reverted(cls, value, values):
        if values.get("closing_remarks"):
            closing_remarks = values.get("closing_remarks", [])
            return value or "rate_added" in closing_remarks
        return False


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
    airline_id: str = None
    commodity: str = None
    commodity_type: str = None
    commodity_sub_type: str = None
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
    rate_type: str = None
    service_provider_id: str
    shipment_type: str = None
    stacking_type: str = None
    surcharge_id: str = None
    validities: list[AirValidities]
    source: str = None
    accuracy: float
    cogo_entity_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None
    height: float = 0
    breadth: float = 0
    length: float = 0
    maximum_weight: float = 0
    currency: str
    discount_type: str = None
    importer_exporter_id: str = None
    rate_not_available_entry: str = None
    rate_created_at: datetime = Field(alias="created_at")
    rate_updated_at: datetime = Field(alias="updated_at")


class AirFreightRateStatistic(BaseModel):
    freight: AirFreight


class ApplyAirFreightRateStatistic(BaseModel):
    action: str
    params: AirFreightRateStatistic = None


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


class FclSelectedForBooking(BaseModel):
    rate_id: str
    validity_id: str


class FclSelectedForPreference(BaseModel):
    rate_id: str = None
    validity_id: str = None
    given_priority: int = 1


class ApplyRevenueDeskFclFreightStatistics(BaseModel):
    shipment_id: str = None
    shipment_fcl_freight_service_id: str = None
    rate_id: str = None
    validities: list[str] = None
    selected_for_booking: FclSelectedForBooking = None
    selected_for_preference: FclSelectedForPreference = None
    action: str = None
    created_at: datetime = datetime.utcnow()

    @validator("created_at", pre=True)
    def convert_created_at(cls, v):
        if not v:
            v = datetime.utcnow()
        return v

class ApplyRevenueDeskAirFreightStatistics(BaseModel):
    shipment_id: str = None
    shipment_air_freight_service_id: str = None
    rate_id: str = None
    validities: list[str] = None
    selected_for_booking: FclSelectedForBooking = None
    selected_for_preference: FclSelectedForPreference = None
    action: str = None
    created_at: datetime = datetime.utcnow()

    @validator("created_at", pre=True)
    def convert_created_at(cls, v):
        if not v:
            v = datetime.utcnow()
        return v
    

class ShipmentAirFreightService(BaseModel):
    shipment_service_id: str = Field(alias="id")
    shipment_service_state: str = Field(alias="state", default=None)
    shipment_service_is_active: bool = Field(alias="is_active", default=None)
    shipment_service_cancellation_reason: str = Field(
        alias="cancellation_reason", default=None
    )
    shipment_service_created_at: datetime = Field(alias="created_at", default=None)
    shipment_service_updated_at: datetime = Field(
        alias="updated_at", default=datetime.utcnow()
    )
    airline_id: str = None
    commodity_type: str = None
    commodity_sub_type: str = None
    height: float = 0
    breadth: float = 0
    length: float = 0
    maximum_weight: float = 0
    operation_type: str = None
    

class SpotSearchAirFreightRateStatistic(BaseModel):
    spot_search_id: str = None
    spot_search_air_freight_service_id: str = None
    rates: list[Rate] = []
    updated_at: datetime
    created_at: datetime
    origin_airport_id: str
    origin_country_id: str = None
    origin_trade_id: str = None
    origin_continent_id: str = None
    destination_airport_id: str
    destination_country_id: str = None
    destination_trade_id: str = None
    destination_continent_id: str = None
    commodity_type: str = None
    commodity_sub_type: str = None
    height: float = 0
    breadth: float = 0
    length: float = 0
    maximum_weight: float = 0
    operation_type: str = None
    importer_exporter_id: str

class CheckoutAirFreightService(BaseModel):
    checkout_id: str
    checkout_air_freight_service_id: str = Field(alias="id")
    rate: CheckoutRate

class AirFreightCheckoutParams(BaseModel):
    checkout_source: str = Field(alias="source")
    checkout_source_id: str = Field(alias="source_id")
    importer_exporter_id: str
    created_at: datetime
    updated_at: datetime
    checkout_air_freight_services: list[CheckoutAirFreightService]
    
class ApplySpotSearchAirFreightRateStatistic(BaseModel):
    action: str
    params: SpotSearchAirFreightRateStatistic

class ApplyCheckoutAirFreightRateStatistic(BaseModel):
    params: AirFreightCheckoutParams = None
    action: str

class AirShipmentParams(BaseModel):
    air_freight_services: list[ShipmentAirFreightService] = []
    shipment: Shipment
    checkout_id: str = None

class ApplyShipmentAirFreightRateStatistics(BaseModel):
    action: str
    params: AirShipmentParams = None
    shipment_update_params: Shipment = None
    shipment_service_update_params: ShipmentAirFreightService = None

class AirQuotationParams(BaseModel):
    fcl_freight_service: ShipmentAirFreightService = None
    buy_quotation: BuyQuotation = None
    shipment: Shipment = None

class ApplyQuotationAirFreightRateStatistics(BaseModel):
    params: list[AirQuotationParams]