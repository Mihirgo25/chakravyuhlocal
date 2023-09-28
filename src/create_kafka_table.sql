
CREATE TABLE brahmastra.kafka_fcl_freight_actions
(
    `data` String
)
ENGINE = Kafka('127.0.0.1:29092', 'arc.public.fcl_freight_actions', '001','JSONAsString')

CREATE MATERIALIZED VIEW brahmastra.fcl_freight_before_actions TO brahmastra.fcl_freight_actions
(
    `id` UInt256,
    `fcl_freight_rate_statistic_id` UInt256,
    `origin_port_id` UUID,
    `destination_port_id` UUID,
    `origin_main_port_id` UUID,
    `destination_main_port_id` UUID,
    `origin_region_id` UUID,
    `destination_region_id` UUID,
    `origin_country_id` UUID,
    `destination_country_id` UUID,
    `origin_continent_id` UUID,
    `destination_continent_id` UUID,
    `origin_trade_id` UUID,
    `destination_trade_id` UUID,
    `commodity` FixedString(256),
    `container_size` FixedString(256),
    `container_type` FixedString(256),
    `service_provider_id` UUID,
    `rate_id` UUID,
    `validity_id` UUID,
    `bas_price` Float64 DEFAULT 0,
    `bas_standard_price` Float64 DEFAULT 0,
    `standard_price` Float64 DEFAULT 0,
    `price Float64` DEFAULT 0,
    `currency` FixedString(3),
    `market_price` Float64 DEFAULT 0,
    `bas_currency` FixedString(3),
    `mode` FixedString(256),
    `parent_mode` FixedString(256),
    `source` FixedString(256),
    `source_id` UUID,
    `sourced_by_id` UUID,
    `procured_by_id` UUID,
    `performed_by_id` UUID,
    `rate_type` FixedString(256),
    `validity_start` DateTime,
    `validity_end` DateTime,
    `shipping_line_id` UUID,
    `importer_exporter_id` UUID,
    `spot_search_id` UUID,
    `spot_search_fcl_freight_service_id` UUID,
    `spot_search` UInt8,
    `checkout_source` FixedString(256),
    `checkout_id` UUID,
    `checkout_fcl_freight_service_id` UUID,
    `checkout` UInt8,
    `checkout_created_at` DateTime,
    `shipment` UInt8,
    `shipment_id` UUID,
    `shipment_source` String,
    `containers_count` UInt8,
    `cargo_weight_per_container` Float64,
    `shipment_state` String,
    `shipment_service_id` UUID,
    `shipment_cancellation_reason` String,
    `shipment_source_id` UUID,
    `shipment_created_at` DateTime,
    `shipment_updated_at` DateTime,
    `shipment_service_state` String,
    `shipment_service_is_active` String, 
    `shipment_service_created_at` DateTime,
    `shipment_service_updated_at` DateTime,
    `shipment_service_cancellation_reason` String,
    `feedback_type` String,
    `feedback_state` String,
    `feedback_ids` Array(UUID),
    `rate_request_state` String,
    `rate_requested_ids` Array(UUID),
    `selected_bas_standard_price` Float64 DEFAULT 0,
    `bas_standard_price_accuracy` Float64 DEFAULT 0,
    `bas_standard_price_diff_from_selected_rate` Float64 DEFAULT 0,
    `selected_fcl_freight_rate_statistic_id` UInt256,
    `selected_rate_id` UUID,
    `selected_validity_id` UUID,
    `selected_type` String,
    `revenue_desk_state` String,
    `given_priority` UInt8,
    `rate_created_at` DateTime,
    `rate_updated_at` DateTime,
    `validity_created_at` DateTime,
    `validity_updated_at` DateTime,
    `created_at` DateTime DEFAULT now(),
    `updated_at` DateTime DEFAULT now(),
    `operation_created_at` DateTime,
    `operation_updated_at` DateTime,
    `sign` Int8 DEFAULT 1,
    `version` UInt8 DEFAULT 1
) AS
SELECT
JSONExtractInt(data, 'before', 'id') AS id,
JSONExtractInt(data, 'before', 'fcl_freight_rate_statistic_id') AS fcl_freight_rate_statistic_id,
JSONExtractString(data, 'before', 'origin_port_id') AS origin_port_id,
JSONExtractString(data, 'before', 'destination_port_id') AS destination_port_id,
JSONExtractString(data, 'before', 'origin_main_port_id') AS origin_main_port_id,
JSONExtractString(data, 'before', 'destination_main_port_id') AS destination_main_port_id,
toUUIDOrZero(JSONExtractString(data, 'before', 'origin_region_id')) AS origin_region_id,
toUUIDOrZero(JSONExtractString(data, 'before', 'destination_region_id')) AS destination_region_id,
JSONExtractString(data, 'before', 'origin_country_id') AS origin_country_id,
JSONExtractString(data, 'before', 'destination_country_id') AS destination_country_id,
JSONExtractString(data, 'before', 'origin_continent_id') AS origin_continent_id,
JSONExtractString(data, 'before', 'destination_continent_id') AS destination_continent_id,
JSONExtractString(data, 'before', 'origin_trade_id') AS origin_trade_id,
JSONExtractString(data, 'before', 'destination_trade_id') AS destination_trade_id,
JSONExtractString(data, 'before', 'commodity') AS commodity,
JSONExtractString(data, 'before', 'container_size') AS container_size,
JSONExtractString(data, 'before', 'container_type') AS container_type,
JSONExtractString(data, 'before', 'service_provider_id') AS service_provider_id,
JSONExtractString(data, 'before', 'rate_id') AS rate_id,
JSONExtractString(data, 'before', 'validity_id') AS validity_id,
JSONExtractFloat(data, 'before', 'bas_price') AS bas_price,
JSONExtractFloat(data, 'before', 'bas_standard_price') AS bas_standard_price,
JSONExtractFloat(data, 'before', 'standard_price') AS standard_price,
JSONExtractFloat(data, 'before', 'price Float64') AS price,  -- Note: There seems to be a space in the column name, which should be removed.
JSONExtractString(data, 'before', 'currency') AS currency,
JSONExtractFloat(data, 'before', 'market_price') AS market_price,
JSONExtractString(data, 'before', 'bas_currency') AS bas_currency,
JSONExtractString(data, 'before', 'mode') AS mode,
JSONExtractString(data, 'before', 'parent_mode') AS parent_mode,
JSONExtractString(data, 'before', 'source') AS source,
JSONExtractString(data, 'before', 'source_id') AS source_id,
JSONExtractString(data, 'before', 'sourced_by_id') AS sourced_by_id,
JSONExtractString(data, 'before', 'procured_by_id') AS procured_by_id,
JSONExtractString(data, 'before', 'performed_by_id') AS performed_by_id,
JSONExtractString(data, 'before', 'rate_type') AS rate_type,
toDate(JSONExtractString(data, 'before', 'validity_start')) AS validity_start,
toDate(JSONExtractString(data, 'before', 'validity_end')) AS validity_end,
JSONExtractString(data, 'before', 'shipping_line_id') AS shipping_line_id,
JSONExtractString(data, 'before', 'importer_exporter_id') AS importer_exporter_id,
JSONExtractString(data, 'before', 'spot_search_id') AS spot_search_id,
JSONExtractString(data, 'before', 'spot_search_fcl_freight_service_id') AS spot_search_fcl_freight_service_id,
JSONExtractInt(data, 'before', 'spot_search') AS spot_search,
JSONExtractString(data, 'before', 'checkout_source') AS checkout_source,
JSONExtractString(data, 'before', 'checkout_id') AS checkout_id,
JSONExtractString(data, 'before', 'checkout_fcl_freight_service_id') AS checkout_fcl_freight_service_id,
JSONExtractInt(data, 'before', 'checkout') AS checkout,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'checkout_created_at')) AS checkout_created_at,
JSONExtractInt(data, 'before', 'shipment') AS shipment,
JSONExtractString(data, 'before', 'shipment_id') AS shipment_id,
JSONExtractString(data, 'before', 'shipment_source') AS shipment_source,
JSONExtractInt(data, 'before', 'containers_count') AS containers_count,
JSONExtractFloat(data, 'before', 'cargo_weight_per_container') AS cargo_weight_per_container,
JSONExtractString(data, 'before', 'shipment_state') AS shipment_state,
JSONExtractString(data, 'before', 'shipment_service_id') AS shipment_service_id,
JSONExtractString(data, 'before', 'shipment_cancellation_reason') AS shipment_cancellation_reason,
JSONExtractString(data, 'before', 'shipment_source_id') AS shipment_source_id,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'shipment_created_at')) AS shipment_created_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'shipment_updated_at')) AS shipment_updated_at,
JSONExtractString(data, 'before', 'shipment_service_state') AS shipment_service_state,
JSONExtractString(data, 'before', 'shipment_service_is_active') AS shipment_service_is_active,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'shipment_service_created_at')) AS shipment_service_created_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'shipment_service_updated_at')) AS shipment_service_updated_at,
JSONExtractString(data, 'before', 'shipment_service_cancellation_reason') AS shipment_service_cancellation_reason,
JSONExtractString(data, 'before', 'feedback_type') AS feedback_type,
JSONExtractString(data, 'before', 'feedback_state') AS feedback_state,
JSONExtractArrayRaw(data, 'before', 'feedback_ids') AS feedback_ids,
JSONExtractString(data, 'before', 'rate_request_state') AS rate_request_state,
JSONExtractArrayRaw(data, 'before', 'rate_requested_ids') AS rate_requested_ids,
JSONExtractFloat(data, 'before', 'selected_bas_standard_price') AS selected_bas_standard_price,
JSONExtractFloat(data, 'before', 'bas_standard_price_accuracy') AS bas_standard_price_accuracy,
JSONExtractFloat(data, 'before', 'bas_standard_price_diff_from_selected_rate') AS bas_standard_price_diff_from_selected_rate,
JSONExtractUInt(data, 'before', 'selected_fcl_freight_rate_statistic_id') AS selected_fcl_freight_rate_statistic_id,
JSONExtractString(data, 'before', 'selected_rate_id') AS selected_rate_id,
JSONExtractString(data, 'before', 'selected_validity_id') AS selected_validity_id,
JSONExtractString(data, 'before', 'selected_type') AS selected_type,
JSONExtractString(data, 'before', 'revenue_desk_state') AS revenue_desk_state,
JSONExtractInt(data, 'before', 'given_priority') AS given_priority,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'rate_created_at')) AS rate_created_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'rate_updated_at')) AS rate_updated_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'validity_created_at')) AS validity_created_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'validity_updated_at')) AS validity_updated_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'created_at')) AS created_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'updated_at')) AS updated_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'operation_created_at')) AS operation_created_at,
parseDateTimeBestEffort(JSONExtractString(data, 'before', 'operation_updated_at')) AS operation_updated_at,
JSONExtractInt(data, 'source', 'lsn') AS version,
-1 AS sign
FROM brahmastra.kafka_fcl_freight_actions
WHERE JSONExtract(data,'op','String') = 'u'

CREATE MATERIALIZED VIEW brahmastra.fcl_freight_after_actions TO brahmastra.fcl_freight_actions
(

    `id` UInt256,
    `fcl_freight_rate_statistic_id` UInt256,
    `origin_port_id` UUID,
    `destination_port_id` UUID,
    `origin_main_port_id` UUID,
    `destination_main_port_id` UUID,
    `origin_region_id` UUID,
    `destination_region_id` UUID,
    `origin_country_id` UUID,
    `destination_country_id` UUID,
    `origin_continent_id` UUID,
    `destination_continent_id` UUID,
    `origin_trade_id` UUID,
    `destination_trade_id` UUID,
    `commodity` FixedString(256),
    `container_size` FixedString(256),
    `container_type` FixedString(256),
    `service_provider_id` UUID,
    `rate_id` UUID,
    `validity_id` UUID,
    `bas_price` Float64 DEFAULT 0,
    `bas_standard_price` Float64 DEFAULT 0,
    `standard_price` Float64 DEFAULT 0,
    `price Float64` DEFAULT 0,
    `currency` FixedString(3),
    `market_price` Float64 DEFAULT 0,
    `bas_currency` FixedString(3),
    `mode` FixedString(256),
    `parent_mode` FixedString(256),
    `source` FixedString(256),
    `source_id` UUID,
    `sourced_by_id` UUID,
    `procured_by_id` UUID,
    `performed_by_id` UUID,
    `rate_type` FixedString(256),
    `validity_start` DateTime,
    `validity_end` DateTime,
    `shipping_line_id` UUID,
    `importer_exporter_id` UUID,
    `spot_search_id` UUID,
    `spot_search_fcl_freight_service_id` UUID,
    `spot_search` UInt8,
    `checkout_source` FixedString(256),
    `checkout_id` UUID,
    `checkout_fcl_freight_service_id` UUID,
    `checkout` UInt8,
    `checkout_created_at` DateTime,
    `shipment` UInt8,
    `shipment_id` UUID,
    `shipment_source` String,
    `containers_count` UInt8,
    `cargo_weight_per_container` Float64,
    `shipment_state` String,
    `shipment_service_id` UUID,
    `shipment_cancellation_reason` String,
    `shipment_source_id` UUID,
    `shipment_created_at` DateTime,
    `shipment_updated_at` DateTime,
    `shipment_service_state` String,
    `shipment_service_is_active` String, 
    `shipment_service_created_at` DateTime,
    `shipment_service_updated_at` DateTime,
    `shipment_service_cancellation_reason` String,
    `feedback_type` String,
    `feedback_state` String,
    `feedback_ids` Array(UUID),
    `rate_request_state` String,
    `rate_requested_ids` Array(UUID),
    `selected_bas_standard_price` Float64 DEFAULT 0,
    `bas_standard_price_accuracy` Float64 DEFAULT 0,
    `bas_standard_price_diff_from_selected_rate` Float64 DEFAULT 0,
    `selected_fcl_freight_rate_statistic_id` UInt256,
    `selected_rate_id` UUID,
    `selected_validity_id` UUID,
    `selected_type` String,
    `revenue_desk_state` String,
    `given_priority` UInt8,
    `rate_created_at` DateTime,
    `rate_updated_at` DateTime,
    `validity_created_at` DateTime,
    `validity_updated_at` DateTime,
    `created_at` DateTime DEFAULT now(),
    `updated_at` DateTime DEFAULT now(),
    `operation_created_at` DateTime,
    `operation_updated_at` DateTime,
    `sign` Int8 DEFAULT 1,
    `version` UInt8 DEFAULT 1

) AS
    SELECT
    JSONExtractInt(data, 'after', 'id') AS id,
    JSONExtractInt(data, 'after', 'fcl_freight_rate_statistic_id') AS fcl_freight_rate_statistic_id,
    JSONExtractString(data, 'after', 'origin_port_id') AS origin_port_id,
    JSONExtractString(data, 'after', 'destination_port_id') AS destination_port_id,
    JSONExtractString(data, 'after', 'origin_main_port_id') AS origin_main_port_id,
    JSONExtractString(data, 'after', 'destination_main_port_id') AS destination_main_port_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'origin_region_id')) AS origin_region_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'destination_region_id')) AS destination_region_id,
    JSONExtractString(data, 'after', 'origin_country_id') AS origin_country_id,
    JSONExtractString(data, 'after', 'destination_country_id') AS destination_country_id,
    JSONExtractString(data, 'after', 'origin_continent_id') AS origin_continent_id,
    JSONExtractString(data, 'after', 'destination_continent_id') AS destination_continent_id,
    JSONExtractString(data, 'after', 'origin_trade_id') AS origin_trade_id,
    JSONExtractString(data, 'after', 'destination_trade_id') AS destination_trade_id,
    JSONExtractString(data, 'after', 'commodity') AS commodity,
    JSONExtractString(data, 'after', 'container_size') AS container_size,
    JSONExtractString(data, 'after', 'container_type') AS container_type,
    JSONExtractString(data, 'after', 'service_provider_id') AS service_provider_id,
    JSONExtractString(data, 'after', 'rate_id') AS rate_id,
    JSONExtractString(data, 'after', 'validity_id') AS validity_id,
    JSONExtractFloat(data, 'after', 'bas_price') AS bas_price,
    JSONExtractFloat(data, 'after', 'bas_standard_price') AS bas_standard_price,
    JSONExtractFloat(data, 'after', 'standard_price') AS standard_price,
    JSONExtractFloat(data, 'after', 'price Float64') AS price,  -- Note: There seems to be a space in the column name, which should be removed.
    JSONExtractString(data, 'after', 'currency') AS currency,
    JSONExtractFloat(data, 'after', 'market_price') AS market_price,
    JSONExtractString(data, 'after', 'bas_currency') AS bas_currency,
    JSONExtractString(data, 'after', 'mode') AS mode,
    JSONExtractString(data, 'after', 'parent_mode') AS parent_mode,
    JSONExtractString(data, 'after', 'source') AS source,
    JSONExtractString(data, 'after', 'source_id') AS source_id,
    JSONExtractString(data, 'after', 'sourced_by_id') AS sourced_by_id,
    JSONExtractString(data, 'after', 'procured_by_id') AS procured_by_id,
    JSONExtractString(data, 'after', 'performed_by_id') AS performed_by_id,
    JSONExtractString(data, 'after', 'rate_type') AS rate_type,
    toDate(JSONExtractString(data, 'after', 'validity_start')) AS validity_start,
    toDate(JSONExtractString(data, 'after', 'validity_end')) AS validity_end,
    JSONExtractString(data, 'after', 'shipping_line_id') AS shipping_line_id,
    JSONExtractString(data, 'after', 'importer_exporter_id') AS importer_exporter_id,
    JSONExtractString(data, 'after', 'spot_search_id') AS spot_search_id,
    JSONExtractString(data, 'after', 'spot_search_fcl_freight_service_id') AS spot_search_fcl_freight_service_id,
    JSONExtractInt(data, 'after', 'spot_search') AS spot_search,
    JSONExtractString(data, 'after', 'checkout_source') AS checkout_source,
    JSONExtractString(data, 'after', 'checkout_id') AS checkout_id,
    JSONExtractString(data, 'after', 'checkout_fcl_freight_service_id') AS checkout_fcl_freight_service_id,
    JSONExtractInt(data, 'after', 'checkout') AS checkout,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'checkout_created_at')) AS checkout_created_at,
    JSONExtractInt(data, 'after', 'shipment') AS shipment,
    JSONExtractString(data, 'after', 'shipment_id') AS shipment_id,
    JSONExtractString(data, 'after', 'shipment_source') AS shipment_source,
    JSONExtractInt(data, 'after', 'containers_count') AS containers_count,
    JSONExtractFloat(data, 'after', 'cargo_weight_per_container') AS cargo_weight_per_container,
    JSONExtractString(data, 'after', 'shipment_state') AS shipment_state,
    JSONExtractString(data, 'after', 'shipment_service_id') AS shipment_service_id,
    JSONExtractString(data, 'after', 'shipment_cancellation_reason') AS shipment_cancellation_reason,
    JSONExtractString(data, 'after', 'shipment_source_id') AS shipment_source_id,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'shipment_created_at')) AS shipment_created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'shipment_updated_at')) AS shipment_updated_at,
    JSONExtractString(data, 'after', 'shipment_service_state') AS shipment_service_state,
    JSONExtractString(data, 'after', 'shipment_service_is_active') AS shipment_service_is_active,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'shipment_service_created_at')) AS shipment_service_created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'shipment_service_updated_at')) AS shipment_service_updated_at,
    JSONExtractString(data, 'after', 'shipment_service_cancellation_reason') AS shipment_service_cancellation_reason,
    JSONExtractString(data, 'after', 'feedback_type') AS feedback_type,
    JSONExtractString(data, 'after', 'feedback_state') AS feedback_state,
    JSONExtractArrayRaw(data, 'after', 'feedback_ids') AS feedback_ids,
    JSONExtractString(data, 'after', 'rate_request_state') AS rate_request_state,
    JSONExtractArrayRaw(data, 'after', 'rate_requested_ids') AS rate_requested_ids,
    JSONExtractFloat(data, 'after', 'selected_bas_standard_price') AS selected_bas_standard_price,
    JSONExtractFloat(data, 'after', 'bas_standard_price_accuracy') AS bas_standard_price_accuracy,
    JSONExtractFloat(data, 'after', 'bas_standard_price_diff_from_selected_rate') AS bas_standard_price_diff_from_selected_rate,
    JSONExtractUInt(data, 'after', 'selected_fcl_freight_rate_statistic_id') AS selected_fcl_freight_rate_statistic_id,
    JSONExtractString(data, 'after', 'selected_rate_id') AS selected_rate_id,
    JSONExtractString(data, 'after', 'selected_validity_id') AS selected_validity_id,
    JSONExtractString(data, 'after', 'selected_type') AS selected_type,
    JSONExtractString(data, 'after', 'revenue_desk_state') AS revenue_desk_state,
    JSONExtractInt(data, 'after', 'given_priority') AS given_priority,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'rate_created_at')) AS rate_created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'rate_updated_at')) AS rate_updated_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'validity_created_at')) AS validity_created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'validity_updated_at')) AS validity_updated_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'created_at')) AS created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'updated_at')) AS updated_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'operation_created_at')) AS operation_created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'operation_updated_at')) AS operation_updated_at,
    JSONExtractFloat(data,'source','lsn') AS version,
    1 AS sign
FROM brahmastra.kafka_fcl_freight_actions  
WHERE JSONExtract(data,'op','String') in ('c','u')


CREATE TABLE brahmastra.fcl_freight_actions
(
    id UInt256,
    fcl_freight_rate_statistic_id UInt256,
    origin_port_id UUID,
    destination_port_id UUID,
    origin_main_port_id UUID,
    destination_main_port_id UUID,
    origin_region_id UUID,
    destination_region_id UUID,
    origin_country_id UUID,
    destination_country_id UUID,
    origin_continent_id UUID,
    destination_continent_id UUID,
    origin_trade_id UUID,
    destination_trade_id UUID,
    commodity FixedString(256),
    container_size FixedString(256),
    container_type FixedString(256),
    service_provider_id UUID,
    rate_id UUID,
    validity_id UUID,
    bas_price Float64 DEFAULT 0,
    bas_standard_price Float64 DEFAULT 0,
    standard_price Float64 DEFAULT 0,
    price Float64 DEFAULT 0,
    currency FixedString(3),
    market_price Float64 DEFAULT 0,
    bas_currency FixedString(3),
    mode FixedString(256),
    parent_mode FixedString(256),
    source FixedString(256),
    source_id UUID,
    sourced_by_id UUID,
    procured_by_id UUID,
    performed_by_id UUID,
    rate_type FixedString(256),
    validity_start DateTime,
    validity_end DateTime,
    shipping_line_id UUID,
    importer_exporter_id UUID,
    spot_search_id UUID,
    spot_search_fcl_freight_service_id UUID,
    spot_search UInt8,
    checkout_source FixedString(256),
    checkout_id UUID,
    checkout_fcl_freight_service_id UUID,
    checkout UInt8,
    checkout_created_at DateTime,
    shipment UInt8,
    shipment_id UUID,
    shipment_source String,
    containers_count UInt8,
    cargo_weight_per_container Float64,
    shipment_state Enum('empty'= 0,'received'= 1,'confirmed_by_importer_exporter'= 2,'cancelled'= 3,'aborted'= 4,'completed'= 5),
    shipment_service_id UUID,
    shipment_cancellation_reason String,
    shipment_source_id UUID,
    shipment_created_at DateTime,
    shipment_updated_at DateTime,
    shipment_service_state Enum('empty'= 0,'containers_gated_out'= 1,'containers_gated_in'= 2,'cancelled'= 3,'awaiting_service_provider_confirmation'= 4,'confirmed_by_service_provider'= 5,'vessel_arrived'= 6,'vessel_departed'= 7,'completed'= 8,'aborted'= 9,'init'= 10),
    shipment_service_is_active String, 
    shipment_service_created_at DateTime,
    shipment_service_updated_at DateTime,
    shipment_service_cancellation_reason String,
    feedback_type Enum('empty'= 0,'disliked'= 1,'liked'= 2),
    feedback_state Enum('empty'= 0,'created'= 1,'closed'= 2,'rate_added'= 3),
    feedback_ids Array(UUID),
    rate_request_state Enum('empty'= 0,'created'= 1,'closed'= 2,'rate_added'= 3),
    rate_requested_ids Array(UUID),
    selected_bas_standard_price Float64 DEFAULT 0,
    bas_standard_price_accuracy Float64 DEFAULT 0,
    bas_standard_price_diff_from_selected_rate Float64 DEFAULT 0,
    selected_fcl_freight_rate_statistic_id UInt256,
    selected_rate_id UUID,
    selected_validity_id UUID,
    selected_type String,
    revenue_desk_state Enum('empty'= 0,'visited'= 1,'selected_for_preference'= 2,'selected_for_booking'= 3),
    given_priority UInt8,
    rate_created_at DateTime,
    rate_updated_at DateTime,
    validity_created_at DateTime,
    validity_updated_at DateTime,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    operation_created_at DateTime,
    operation_updated_at DateTime,
    sign Int8 DEFAULT 1,
    version UInt8 DEFAULT 1
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_continent_id, parent_mode,origin_country_id, container_size, origin_port_id, rate_id, id)
ORDER BY (origin_continent_id, parent_mode, origin_country_id, container_size, origin_port_id , rate_id, id, version);