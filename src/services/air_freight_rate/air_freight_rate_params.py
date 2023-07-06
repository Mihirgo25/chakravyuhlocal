from pydantic import BaseModel
from datetime import datetime, date
from peewee import *
from typing import List


class CreateDraftAirFreightRateParams(BaseModel):
    source: str
    rate_id: str = None
    source: str
    origin_airport_id: str
    destination_airport_id: str
    weight_slabs: dict
    min_price: float
    meta_data: dict = {}
    commodity: str
    commodity_type: str = None
    operation_type: str
    price_type: str
    rate_type: str = None
    service_provider_id: str
    airline_id: str
    currency: str
    stacking_type: str
    status: str = "active"
    source: str
    validity_start: datetime
    validity_end: datetime


class WeightSlab(BaseModel):
    lower_limit: float
    upper_limit: float
    tariff_price: float
    currency: str
    unit: str = "per_kg"


class Slab(BaseModel):
    lower_limit: float
    upper_limit: float
    price: float
    currency: str


class Item(BaseModel):
    packing_type: str = None
    handling_type: str = None
    packages_count: int = None
    package_weight: float = None
    height: float = None
    length: float = None
    width: float = None


class LineItem(BaseModel):
    code: str
    unit: str
    price: float
    currency: str
    min_price: float
    remarks: list[str] = []


class TaskLineItem(BaseModel):
    location_id: str = None
    code: str
    unit: str
    price: float
    currency: str
    min_price: float = None
    remarks: list[str] = None
    slabs: list[Slab] = None


class LineItemLocal(BaseModel):
    code: str
    unit: str
    min_price: float
    price: float
    currency: str
    remarks: list[str] = []
    slabs: list[Slab] = []


class LocalData(BaseModel):
    line_items: list[TaskLineItem] = None


class DeleteAirFreightRateParams(BaseModel):
    id: str
    validity_id: str
    performed_by_id: str
    performed_by_type: str = None
    bulk_operation_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None


class UpdateAirFreightRateParams(BaseModel):
    id: str
    validity_id: str
    validity_start: date = None
    validity_end: date = None
    currency: str = None
    min_price: float
    performed_by_id: str = None
    performed_by_type: str = None
    bulk_operation_id: str = None
    weight_slabs: list[WeightSlab]
    length: float = None
    breadth: float = None
    height: float = None
    maximum_weight: float = None
    procured_by_id: str = None
    sourced_by_id: str = None
    available_volume: float = None
    available_gross_weight: float = None


class CreateAirFreightRateSurchargeParams(BaseModel):
    origin_airport_id: str
    destination_airport_id: str
    commodity: str
    commodity_type: str
    airline_id: str
    operation_type: str
    service_provider_id: str
    performed_by_id: str = None
    performed_by_type: str = None
    procured_by_id: str
    sourced_by_id: str
    bulk_operation_id: str = None
    rate_sheet_id: str = None
    line_items: list[LineItem]


class UpdateAirFreightRateSurchargeParams(BaseModel):
    id: str
    performed_by_id: str = None
    procured_by_id: str = None
    sourced_by_id: str = None
    line_items: list[LineItem]


class ListSlab(BaseModel):
    lower_limit: int
    upper_limit: int
    price: float
    currency: str


class CreateAirFreightRateLocalParams(BaseModel):
    airport_id: str
    airline_id: str
    trade_type: str
    commodity: str
    commodity_type: str
    service_provider_id: str
    performed_by_id: str = None
    procured_by_id: str
    sourced_by_id: str
    bulk_operation_id: str = None
    rate_sheet_id: str = None
    rate_type: str = "market_place"
    line_items: list[LineItemLocal]


class LocalSlabsParams(BaseModel):
    lower_limit: int
    upper_limit: int
    price: float
    currency: str


class LineItemsLocalParams(BaseModel):
    code: str
    unit: str
    price: float
    min_price: float
    currency: str
    remarks: list[str] = None
    slabs: list[LocalSlabsParams] = None


class UpdateAirFrieghtRateLocalParams(BaseModel):
    id: str
    performed_by_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None
    bulk_operation_id: str = None
    line_items: list[LineItemsLocalParams] = None


class CreateAirFrieghtRateNotAvailableParams(BaseModel):
    origin_airport_id: str
    origin_country_id: str
    origin_trade_id: str
    destination_airport_id: str
    destination_country_id: str
    destination_trade_id: str
    commodity: str


class CreateAirFreightRateTaskParams(BaseModel):
    service: str
    airport_id: str
    commodity: str
    commodity_type: str
    trade_type: str
    airline_id: str
    logistics_service_type: str
    source: str
    task_type: str
    shipment_id: str = None
    performed_by_id: str
    performed_by_type: str = None
    rate: LocalData = None


class UpdateAirFreightRateTaskParams(BaseModel):
    id: str
    performed_by_id: str = None
    performed_by_type: str = None
    rate: LocalData = None
    status: str = None
    closing_remarks: str = None


class CreateAirFreightRateFeedbackParams(BaseModel):
    source: str
    source_id: str
    performed_by_id: str
    performed_by_org_id: str
    performed_by_type: str
    rate_id: str
    validity_id: str
    likes_count: int
    dislikes_count: int
    feedbacks: list[str] = []
    remarks: list[str] = []
    preferred_freight_rate: float = None
    preferred_freight_rate_currency: str = None
    preferred_airline_ids: list[str] = []
    preferred_storage_free_days: int = None
    feedback_type: str
    booking_params: dict = {}
    trade_type: str = None
    origin_airport_id: str = None
    origin_country_id: str = None
    origin_continent_id: str = None
    origin_trade_id: str = None
    destination_airport_id: str = None
    destination_trade_id: str = None
    destination_country_id: str = None
    destination_continent_id: str = None
    service_provider_id: str = None
    cogo_entity_id: str = None
    operation_type: str = None
    airline_id: str = None
    commodity: str = None


class CreateAirFreightRateRequestParams(BaseModel):
    source: str
    source_id: str
    cogo_entity_id: str
    performed_by_id: str
    performed_by_org_id: str
    performed_by_type: str = None
    preferred_freight_rate: float = None
    preferred_freight_rate_currency: str = None
    preferred_detention_free_days: int = None
    preferred_storage_free_days: int = None
    cargo_readiness_date: date = None
    preferred_airline_ids: list[str] = []
    remarks: list[str] = []
    booking_params: dict = {}
    weight: float
    volume: float
    inco_term: str
    commodity: str = None
    commodity_type: str = None
    commodity_sub_type: str = None
    cargo_stacking_type: str = None
    packages_count: int = None
    trade_type: str = None
    service_provider_id: str = None
    price_type: str = None
    operation_type: str = None
    destination_continent_id: str = None
    destination_country_id: str = None
    destination_airport_id: str
    destination_trade_id: str = None
    origin_continent_id: str = None
    origin_country_id: str = None
    origin_airport_id: str
    origin_trade_id: str = None
    packages: list[Item] = None
    airline_id: str = None


class WarehouseLineItemsParams(BaseModel):
    code: str
    unit: str
    min_price: float
    currency: str
    remarks: list = []
    slabs: list[Slab] = None


class CreateAirFreightWarehouseRatesParams(BaseModel):
    airport_id: str
    trade_type: str
    commodity: str
    service_provider_id: str
    performed_by_id: str
    procured_by_id: str
    sourced_by_id: str
    bulk_operation_id: str = None
    rate_sheet_id: str = None
    line_items: list[WarehouseLineItemsParams] = None


class UpdateAirFreightStorageRatesParams(BaseModel):
    id: str
    performed_by_id: str
    bulk_operation_id: str = None
    free_limit: int = None
    slabs: list[Slab] = None


class UpdateAirFreightRateMarkUpParams(BaseModel):
    id: str
    performed_by_id: str
    bulk_operation_id: str = None
    validity_id: str = None
    validity_start: datetime = None
    validity_end: datetime = None


class AddFreightRateMarkupParams(BaseModel):
    markup: float
    markup_type: str
    markup_currency: str = None
    validity_id: str = None
    air_freight_rate_id: str


class DeleteFreightRateParams(BaseModel):
    air_freight_rate_id: str
    validity_id: str = None
    
class UpdateFreightRateParams(BaseModel):
    validity_id: str = None
    air_freight_rate_id: str
    new_start_date: datetime
    new_end_date: datetime


class DeleteAirFreightRateLocalParams(BaseModel):
    air_freight_rate_local_id: str


class DeleteAirFreightRateSurchargeParams(BaseModel):
    air_freight_rate_surcharge_id: str


class CreateBulkOperationParams(BaseModel):
    performed_by_id: str = None
    performed_by_type: str = None
    add_freight_rate_markup: List[AddFreightRateMarkupParams] = None
    delete_freight_rate: List[DeleteFreightRateParams] = None
    add_freight_rate_markup: List[AddFreightRateMarkupParams] = None
    update_freight_rate: List[UpdateFreightRateParams] = None
    delete_freight_rate_local: List[DeleteAirFreightRateLocalParams] = None
    delete_freight_rate_surcharge: List[DeleteAirFreightRateSurchargeParams] = None


class CreateAirFreightRateParams(BaseModel):
    origin_airport_id: str
    destination_airport_id: str
    commodity: str
    commodity_type: str
    commodity_sub_type: str = None
    airline_id: str
    operation_type: str
    currency: str
    price_type: str
    min_price: float = 0
    service_provider_id: str
    density_category: str = "general"
    density_ratio: str = None
    bulk_operation_id: str = None
    rate_sheet_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    procured_by_id: str
    sourced_by_id: str
    cogo_entity_id: str = None
    length: int = 300
    breadth: int = 300
    height: int = 300
    maximum_weight: int = 20000
    shipment_type: str = "box"
    stacking_type: str = "stackable"
    rate_type: str = "market_place"
    initial_volume: float = None
    initial_gross_weight: float = None
    available_volume: float = None
    available_gross_weight: float = None
    weight_slabs: list[WeightSlab]
    validity_start: datetime
    validity_end: datetime
    external_rate_id: str = None
    mode: str = 'manual'
    flight_uuid: str = None
    air_freight_rate_request_id: str = None


class DeleteAirFreightRateFeedbackParams(BaseModel):
    air_freight_rate_feedback_ids: List[str]
    closing_remarks: List[str] = []
    performed_by_id: str = None
    reverted_rate_id: str = None
    reverted_validity_id: str = None


class CreateAirFreightStorageRateParams(BaseModel):
    rate_sheet_id: str = None
    performed_by_id: str
    procured_by_id: str
    sourced_by_id: str
    airport_id: str
    airline_id: str
    trade_type: str
    commodity: str
    service_provider_id: str
    free_limit: int
    remarks: list[str] = []
    slabs: list[Slab] = None


class UpdateAirFreightWarehouseRateParams(BaseModel):
    id: str
    performed_by_id: str = None
    line_items: list[WarehouseLineItemsParams] = None


class UpdateAirFreightRateRequestParams(BaseModel):
    air_freight_rate_request_id: str
    closing_remarks: list[str] = None
    status: str=None
    remarks: str=None
    performed_by_id: str


class DeleteAirFreightRateRequestParams(BaseModel):
    air_freight_rate_request_ids: list[str]
    closing_remarks: list[str] = None
    rate_id: str = None
    validity_id: str = None
    performed_by_id: str = None