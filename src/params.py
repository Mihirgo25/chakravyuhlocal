from pydantic import BaseModel
from typing import List

class GetFclFreightRate(BaseModel):
    origin_port_id: str = None
    origin_main_port_id: str = None
    destination_port_id: str = None
    destination_main_port_id: str = None
    container_size: str = None
    container_type: str = None
    commodity: str = True
    shipping_line_id: str = None
    service_provider_id: str = None
    importer_exporter_id: str = None

class GetFclFreightRateLocal(BaseModel):
    port_id: str = None
    main_port_id: str = None
    trade_type: str = None
    container_size: str = None
    container_type: str = None
    commodity: str = None
    shipping_line_id: str = None
    service_provider_id: str = None

# class PossibleDirectFilters(BaseModel):
#     id: str = None
#     origin_port_id: str = None
#     origin_country_id: str = None
#     origin_trade_id: str = None
#     origin_continent_id: str = None
#     destination_port_id: str = None
#     destination_country_id: str = None
#     destination_trade_id: str = None
#     destination_continent_id: str = None
#     shipping_line_id: str = None
#     service_provider_id: str = None
#     importer_exporter_id: str = None
#     container_size: str = None
#     container_type: str = None
#     commodity: str = None
#     is_best_price: str = None
#     rate_not_available_entry: str = None
#     origin_main_port_id: str = None
#     destination_main_port_id: str = None
#     cogo_entity_id: str = None

# class PossibleIndirectFilters(BaseModel):
#     is_origin_local_missing: str = None
#     is_destination_local_missing: str = None
#     is_weight_limit_missing: str = None
#     is_origin_detention_missing: str = None
#     is_origin_plugin_missing: str = None
#     is_destination_detention_missing: str = None
#     is_destination_demurrage_missing: str = None
#     is_destination_plugin_missing: str = None
#     is_rate_about_to_expire: str = None
#     is_rate_available: str = None
#     is_rate_not_available: str = None
#     origin_location_ids: str = None
#     destination_location_ids: str = None
#     importer_exporter_present: str = None
#     last_rate_available_date_greater_than: str = None
#     validity_start_greater_than: str = None
#     validity_end_less_than: str = None
#     procured_by_id: str = None

# class ListFclFreightRate(BaseModel):
#     filters: str = None
#     page_limit: int = 10
#     page: int = 1
#     sort_by: str = 'priority_score'
#     sort_type: str = 'desc'
#     pagination_data_required: bool = True
#     return_query: bool = False
#     expired_rates_required: bool = False

class GetFclFreightRateCard(BaseModel):
    origin_port_id: str
    origin_country_id: str
    destination_port_id: str
    destination_country_id: str
    container_size: str
    container_type: str
    commodity: str
    importer_exporter_id: str
    containers_count: int
    bls_count: int
    include_origin_local: bool
    include_destination_local: bool
    trade_type: str
    include_destination_dpd: bool
    cargo_weight_per_container: int = 0
    additional_services: List[str] = []
    validity_start: str
    validity_end: str
    ignore_omp_dmp_sl_sps: List[str] = []
    include_confirmed_inventory_rates: bool = False
    cogo_entity_id: str = None

class GetFclFreightLocalRateCards(BaseModel):
    trade_type: str
    port_id: str
    country_id: str
    shipping_line_id: str = None
    container_size: str
    container_type: str
    commodity: str = None
    containers_count: int 
    bls_count: int
    cargo_weight_per_container: int = None
    include_destination_dpd: bool = False
    additional_services: List[str] = []
    include_confirmed_inventory_rates: bool = False
    rates: List[str] = []
    service_provider_id: str = None

class DeleteFclFreightRate(BaseModel):
    id: str
    performed_by_id: str
    bulk_operation_id: str = None
    sourced_by_id: str 
    procured_by_id: str

class DeleteFclFreightRateFeedback(BaseModel):
    fcl_freight_rate_feedback_ids: List[str]
    closing_remarks: List[str] = []
    performed_by_id: str

#   string :source
#   string :source_id
#   string :performed_by_id
#   string :performed_by_org_id
#   string :performed_by_type
#   string :rate_id
#   string :validity_id
#   integer :likes_count
#   integer :dislikes_count
#   array :feedbacks, default: [] do
#     string    
#   end
#   array :remarks, default: [] do
#     string    
#   end
#   float :preferred_freight_rate, default: nil
#   string :preferred_freight_rate_currency, default: nil
#   integer :preferred_detention_free_days, default: nil
#   array :preferred_shipping_line_ids, default: [] do
#     string    
#   end
#   string :feedback_type
#   hash :booking_params, default: {}, strip: false

class CreateFclFreightRateNotAvailable(BaseModel):
    origin_port_id: str
    origin_country_id: str = None
    origin_trade_id: str = None
    destination_port_id: str
    destination_country_id: str = None
    destination_trade_id: str = None
    container_size: str
    container_type: str
    commodity: str