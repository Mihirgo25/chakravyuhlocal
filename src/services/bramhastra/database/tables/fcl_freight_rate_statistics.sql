
CREATE TABLE brahmastra.kafka_fcl_freight_rate_statistics
(
    `data` String
)
ENGINE = Kafka('127.0.0.1:29092', 'arc.public.fcl_freight_rate_statistics', '001','JSONAsString');

CREATE MATERIALIZED VIEW brahmastra.fcl_freight_before_rate_statistics TO brahmastra.fcl_freight_rate_statistics
(
    `id` UInt256,
    `identifier` FixedString(256),
    `validity_id` UUID,
    `rate_id` UUID,
    `payment_term` FixedString(256),
    `schedule_type` FixedString(256),
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
    `origin_pricing_zone_map_id` UUID,
    `destination_pricing_zone_map_id` UUID,
    `price` Float64,    
    `standard_price` Float64,     
    `market_price` Float64,
    `validity_start` Date,
    `validity_end` Date,
    `currency` FixedString(3),
    `shipping_line_id` UUID,
    `service_provider_id` UUID,
    `mode` FixedString(256),
    `likes_count` UInt16 DEFAULT 0,
    `dislikes_count` UInt16 DEFAULT 0,
    `spot_search_count` UInt16 DEFAULT 0,
    `checkout_count` UInt16 DEFAULT 0,
    `bookings_created` UInt16 DEFAULT 0,
    `rate_created_at` DateTime DEFAULT now(),
    `rate_updated_at` DateTime DEFAULT now(),
    `validity_created_at` DateTime DEFAULT now(),
    `validity_updated_at` DateTime DEFAULT now(),
    `commodity` FixedString(256),
    `container_size` String,
    `container_type` FixedString(256),
    `containers_count` UInt8 DEFAULT 0,
    `origin_local_id` UUID,
    `destination_local_id` UUID,
    `applicable_origin_local_count` UInt16 DEFAULT 0,
    `applicable_destination_local_count` UInt16 DEFAULT 0,
    `origin_detention_id` UUID,
    `destination_detention_id` UUID,
    `origin_demurrage_id` UUID,
    `destination_demurrage_id` UUID,
    `cogo_entity_id` UUID,
    `rate_type` FixedString(256),
    `sourced_by_id` UUID,
    `procured_by_id` UUID,
    `revenue_desk_visit_count` UInt16,
    `so1_visit_count` UInt16,
    `created_at` DateTime DEFAULT now(),
    `updated_at` DateTime DEFAULT now(),
    `version` UInt64,
    `sign` Int8,
    `status` FixedString(10) DEFAULT 'active',
    `last_action` FixedString(10) DEFAULT 'create',
    `parent_rate_id` UUID,
    `parent_validity_id` UUID,
    `so1_select_count` UInt16,
    `parent_mode` FixedString(255),
    `source` String,
    `source_id` UUID,
    `performed_by_id` UUID,
    `performed_by_type` FixedString(256),
    `rate_sheet_id` UUID,
    `bulk_operation_id` UUID,
    `operation_created_at` DateTime,
    `operation_updated_at` DateTime,
    `is_deleted` Bool DEFAULT false,
    `bas_price` Float64,
    `bas_standard_price` Float64,
    `bas_currency` FixedString(3),
    `tag` FixedString(256),
    `shipment_completed` UInt16,
    `shipment_cancelled` UInt16,
    `bas_standard_price_accuracy` Float64,
    `bas_standard_price_diff_from_selected_rate` Float64,
    `parent_rate_mode` String
) AS
SELECT
    JSONExtractInt(data, 'before', 'id') AS id,
    JSONExtractString(data, 'before', 'identifier') AS identifier,
    toUUIDOrZero(JSONExtractString(data, 'before', 'validity_id')) AS validity_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'rate_id')) AS rate_id,
    JSONExtractString(data, 'before', 'payment_term') AS payment_term,
    JSONExtractString(data, 'before', 'schedule_type') AS schedule_type,
    JSONExtractString(data, 'before', 'origin_port_id') AS origin_port_id,
    JSONExtractString(data, 'before', 'destination_port_id') AS destination_port_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'origin_main_port_id')) AS origin_main_port_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'destination_main_port_id')) AS destination_main_port_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'origin_region_id')) AS origin_region_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'destination_region_id')) AS destination_region_id,
    JSONExtractString(data, 'before', 'origin_country_id') AS origin_country_id,
    JSONExtractString(data, 'before', 'destination_country_id') AS destination_country_id,
    JSONExtractString(data, 'before', 'origin_continent_id') AS origin_continent_id,
    JSONExtractString(data, 'before', 'destination_continent_id') AS destination_continent_id,
    JSONExtractString(data, 'before', 'origin_trade_id') AS origin_trade_id,
    JSONExtractString(data, 'before', 'destination_trade_id') AS destination_trade_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'origin_pricing_zone_map_id')) AS origin_pricing_zone_map_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'destination_pricing_zone_map_id')) AS destination_pricing_zone_map_id,
    JSONExtractFloat(data, 'before', 'price') AS price,
    JSONExtractFloat(data, 'before', 'standard_price') AS standard_price,
    JSONExtractFloat(data, 'before', 'market_price') AS market_price,
    toDate(JSONExtractInt(data, 'before', 'validity_start')) AS validity_start,
    toDate(JSONExtractInt(data, 'before', 'validity_end')) AS validity_end,
    JSONExtractString(data, 'before', 'currency') AS currency,
    JSONExtractString(data, 'before', 'shipping_line_id') AS shipping_line_id,
    JSONExtractString(data, 'before', 'service_provider_id') AS service_provider_id,
    JSONExtractString(data, 'before', 'mode') AS mode,
    JSONExtractInt(data, 'before', 'likes_count') AS likes_count,
    JSONExtractInt(data, 'before', 'dislikes_count') AS dislikes_count,
    JSONExtractInt(data, 'before', 'spot_search_count') AS spot_search_count,
    JSONExtractInt(data, 'before', 'checkout_count') AS checkout_count,
    JSONExtractInt(data, 'before', 'bookings_created') AS bookings_created,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'before', 'rate_created_at')) AS rate_created_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'before', 'rate_updated_at')) AS rate_updated_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'before', 'validity_created_at')) AS validity_created_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'before', 'validity_updated_at')) AS validity_updated_at,
    JSONExtractString(data, 'before', 'commodity') AS commodity,
    JSONExtractString(data, 'before', 'container_size') AS container_size,
    JSONExtractString(data, 'before', 'container_type') AS container_type,
    JSONExtractInt(data, 'before', 'containers_count') AS containers_count,
    toUUIDOrZero(JSONExtractString(data, 'before', 'origin_local_id')) AS origin_local_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'destination_local_id')) AS destination_local_id,
    JSONExtractInt(data, 'before', 'applicable_origin_local_count') AS applicable_origin_local_count,
    JSONExtractInt(data, 'before', 'applicable_destination_local_count') AS applicable_destination_local_count,
    toUUIDOrZero(JSONExtractString(data, 'before', 'origin_detention_id')) AS origin_detention_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'destination_detention_id')) AS destination_detention_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'origin_demurrage_id')) AS origin_demurrage_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'destination_demurrage_id')) AS destination_demurrage_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'cogo_entity_id')) AS cogo_entity_id,
    JSONExtractString(data, 'before', 'rate_type') AS rate_type,
    toUUIDOrZero(JSONExtractString(data, 'before', 'sourced_by_id')) AS sourced_by_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'procured_by_id')) AS procured_by_id,
    JSONExtractInt(data, 'before', 'revenue_desk_visit_count') AS revenue_desk_visit_count,
    JSONExtractInt(data, 'before', 'so1_visit_count') AS so1_visit_count,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'before', 'created_at')) AS created_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'before', 'updated_at')) AS updated_at,
    toUnixTimestamp64Milli(parseDateTime64BestEffort(visitParamExtractString(visitParamExtractRaw(data, 'before'), 'operation_updated_at'), 6)) AS version,
    -1 AS sign,
    JSONExtractString(data, 'before', 'status') AS status,
    JSONExtractString(data, 'before', 'last_action') AS last_action,
    toUUIDOrZero(JSONExtractString(data, 'before', 'parent_rate_id')) AS parent_rate_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'parent_validity_id')) AS parent_validity_id,
    JSONExtractInt(data, 'before', 'so1_select_count') AS so1_select_count,
    JSONExtractString(data, 'before', 'parent_mode') AS parent_mode,
    JSONExtractString(data, 'before', 'source') AS source,
    toUUIDOrZero(JSONExtractString(data, 'before', 'source_id')) AS source_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'performed_by_id')) AS performed_by_id,
    JSONExtractString(data, 'before', 'performed_by_type') AS performed_by_type,
    toUUIDOrZero(JSONExtractString(data, 'before', 'rate_sheet_id')) AS rate_sheet_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'bulk_operation_id')) AS bulk_operation_id,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'before', 'operation_created_at')) AS operation_created_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'before', 'operation_updated_at')) AS operation_updated_at,
    JSONExtractString(data, 'before', 'is_deleted') AS is_deleted,
    JSONExtractFloat(data, 'before', 'bas_price') AS bas_price,
    JSONExtractFloat(data, 'before', 'bas_standard_price') AS bas_standard_price,
    JSONExtractString(data, 'before', 'bas_currency') AS bas_currency,
    JSONExtractString(data, 'before', 'tag') AS tag,
    JSONExtractInt(data, 'before', 'shipment_completed') AS shipment_completed,
    JSONExtractInt(data, 'before', 'shipment_cancelled') AS shipment_cancelled,
    JSONExtractFloat(data, 'before', 'bas_standard_price_accuracy') AS bas_standard_price_accuracy,
    JSONExtractFloat(data, 'before', 'bas_standard_price_diff_from_selected_rate') AS bas_standard_price_diff_from_selected_rate,
    JSONExtractString(data, 'before', 'parent_rate_mode') AS parent_rate_mode
    FROM brahmastra.kafka_fcl_freight_rate_statistics
    WHERE JSONExtractString(data,'op') = 'u';

CREATE MATERIALIZED VIEW brahmastra.fcl_freight_after_rate_statistics TO brahmastra.fcl_freight_rate_statistics
(
    `id` UInt256,
    `identifier` FixedString(256),
    `validity_id` UUID,
    `rate_id` UUID,
    `payment_term` FixedString(256),
    `schedule_type` FixedString(256),
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
    `origin_pricing_zone_map_id` UUID,
    `destination_pricing_zone_map_id` UUID,
    `price` Float64,    
    `standard_price` Float64,     
    `market_price` Float64,
    `validity_start` Date,
    `validity_end` Date,
    `currency` FixedString(3),
    `shipping_line_id` UUID,
    `service_provider_id` UUID,
    `mode` FixedString(256),
    `likes_count` UInt16 DEFAULT 0,
    `dislikes_count` UInt16 DEFAULT 0,
    `spot_search_count` UInt16 DEFAULT 0,
    `checkout_count` UInt16 DEFAULT 0,
    `bookings_created` UInt16 DEFAULT 0,
    `rate_created_at` DateTime DEFAULT now(),
    `rate_updated_at` DateTime DEFAULT now(),
    `validity_created_at` DateTime DEFAULT now(),
    `validity_updated_at` DateTime DEFAULT now(),
    `commodity` FixedString(256),
    `container_size` String,
    `container_type` FixedString(256),
    `containers_count` UInt8 DEFAULT 0,
    `origin_local_id` UUID,
    `destination_local_id` UUID,
    `applicable_origin_local_count` UInt16 DEFAULT 0,
    `applicable_destination_local_count` UInt16 DEFAULT 0,
    `origin_detention_id` UUID,
    `destination_detention_id` UUID,
    `origin_demurrage_id` UUID,
    `destination_demurrage_id` UUID,
    `cogo_entity_id` UUID,
    `rate_type` FixedString(256),
    `sourced_by_id` UUID,
    `procured_by_id` UUID,
    `revenue_desk_visit_count` UInt16,
    `so1_visit_count` UInt16,
    `created_at` DateTime DEFAULT now(),
    `updated_at` DateTime DEFAULT now(),
    `version` UInt64 DEFAULT 1,
    `sign` Int8,
    `status` FixedString(10) DEFAULT 'active',
    `last_action` FixedString(10) DEFAULT 'create',
    `parent_rate_id` UUID,
    `parent_validity_id` UUID,
    `so1_select_count` UInt16,
    `parent_mode` FixedString(255),
    `source` String,
    `source_id` UUID,
    `performed_by_id` UUID,
    `performed_by_type` FixedString(256),
    `rate_sheet_id` UUID,
    `bulk_operation_id` UUID,
    `operation_created_at` DateTime,
    `operation_updated_at` DateTime,
    `is_deleted` Bool DEFAULT false,
    `bas_price` Float64,
    `bas_standard_price` Float64,
    `bas_currency` FixedString(3),
    `tag` FixedString(256),
    `shipment_completed` UInt16,
    `shipment_cancelled` UInt16,
    `bas_standard_price_accuracy` Float64,
    `bas_standard_price_diff_from_selected_rate` Float64,
    `parent_rate_mode` String
) AS
    SELECT
    JSONExtractInt(data, 'after', 'id') AS id,
    JSONExtractString(data, 'after', 'identifier') AS identifier,
    JSONExtractString(data, 'after', 'validity_id') AS validity_id,
    JSONExtractString(data, 'after', 'rate_id') AS rate_id,
    JSONExtractString(data, 'after', 'payment_term') AS payment_term,
    JSONExtractString(data, 'after', 'schedule_type') AS schedule_type,
    JSONExtractString(data, 'after', 'origin_port_id') AS origin_port_id,
    JSONExtractString(data, 'after', 'destination_port_id') AS destination_port_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'origin_main_port_id')) AS origin_main_port_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'destination_main_port_id')) AS destination_main_port_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'origin_region_id')) AS origin_region_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'destination_region_id')) AS destination_region_id,
    JSONExtractString(data, 'after', 'origin_country_id') AS origin_country_id,
    JSONExtractString(data, 'after', 'destination_country_id') AS destination_country_id,
    JSONExtractString(data, 'after', 'origin_continent_id') AS origin_continent_id,
    JSONExtractString(data, 'after', 'destination_continent_id') AS destination_continent_id,
    JSONExtractString(data, 'after', 'origin_trade_id') AS origin_trade_id,
    JSONExtractString(data, 'after', 'destination_trade_id') AS destination_trade_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'origin_pricing_zone_map_id')) AS origin_pricing_zone_map_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'destination_pricing_zone_map_id')) AS destination_pricing_zone_map_id,
    JSONExtractFloat(data, 'after', 'price') AS price,
    JSONExtractFloat(data, 'after', 'standard_price') AS standard_price,
    JSONExtractFloat(data, 'after', 'market_price') AS market_price,
    toDate(JSONExtractInt(data, 'after', 'validity_start')) AS validity_start,
    toDate(JSONExtractInt(data, 'after', 'validity_end')) AS validity_end,
    JSONExtractString(data, 'after', 'currency') AS currency,
    JSONExtractString(data, 'after', 'shipping_line_id') AS shipping_line_id,
    JSONExtractString(data, 'after', 'service_provider_id') AS service_provider_id,
    JSONExtractString(data, 'after', 'mode') AS mode,
    JSONExtractInt(data, 'after', 'likes_count') AS likes_count,
    JSONExtractInt(data, 'after', 'dislikes_count') AS dislikes_count,
    JSONExtractInt(data, 'after', 'spot_search_count') AS spot_search_count,
    JSONExtractInt(data, 'after', 'checkout_count') AS checkout_count,
    JSONExtractInt(data, 'after', 'bookings_created') AS bookings_created,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'after', 'rate_created_at')) AS rate_created_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'after', 'rate_updated_at')) AS rate_updated_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'after', 'validity_created_at')) AS validity_created_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'after', 'validity_updated_at')) AS validity_updated_at,
    JSONExtractString(data, 'after', 'commodity') AS commodity,
    JSONExtractString(data, 'after', 'container_size') AS container_size,
    JSONExtractString(data, 'after', 'container_type') AS container_type,
    JSONExtractInt(data, 'after', 'containers_count') AS containers_count,
    toUUIDOrZero(JSONExtractString(data, 'after', 'origin_local_id')) AS origin_local_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'destination_local_id')) AS destination_local_id,
    JSONExtractInt(data, 'after', 'applicable_origin_local_count') AS applicable_origin_local_count,
    JSONExtractInt(data, 'after', 'applicable_destination_local_count') AS applicable_destination_local_count,
    toUUIDOrZero(JSONExtractString(data, 'after', 'origin_detention_id')) AS origin_detention_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'destination_detention_id')) AS destination_detention_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'origin_demurrage_id')) AS origin_demurrage_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'destination_demurrage_id')) AS destination_demurrage_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'cogo_entity_id')) AS cogo_entity_id,
    JSONExtractString(data, 'after', 'rate_type') AS rate_type,
    toUUIDOrZero(JSONExtractString(data, 'after', 'sourced_by_id')) AS sourced_by_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'procured_by_id')) AS procured_by_id,
    JSONExtractInt(data, 'after', 'revenue_desk_visit_count') AS revenue_desk_visit_count,
    JSONExtractInt(data, 'after', 'so1_visit_count') AS so1_visit_count,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'after', 'created_at')) AS created_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'after', 'updated_at')) AS updated_at,
    toUnixTimestamp64Milli(parseDateTime64BestEffort(visitParamExtractString(visitParamExtractRaw(data, 'after'), 'operation_updated_at'), 6)) AS version,
    1 AS sign,
    JSONExtractString(data, 'after', 'status') AS status,
    JSONExtractString(data, 'after', 'last_action') AS last_action,
    toUUIDOrZero(JSONExtractString(data, 'after', 'parent_rate_id')) AS parent_rate_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'parent_validity_id')) AS parent_validity_id,
    JSONExtractInt(data, 'after', 'so1_select_count') AS so1_select_count,
    JSONExtractString(data, 'after', 'parent_mode') AS parent_mode,
    JSONExtractString(data, 'after', 'source') AS source,
    toUUIDOrZero(JSONExtractString(data, 'after', 'source_id')) AS source_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'performed_by_id')) AS performed_by_id,
    JSONExtractString(data, 'after', 'performed_by_type') AS performed_by_type,
    toUUIDOrZero(JSONExtractString(data, 'after', 'rate_sheet_id')) AS rate_sheet_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'bulk_operation_id')) AS bulk_operation_id,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'after', 'operation_created_at')) AS operation_created_at,
    parseDateTimeBestEffortOrZero(JSONExtractString(data, 'after', 'operation_updated_at')) AS operation_updated_at,
    JSONExtractString(data, 'after', 'is_deleted') AS is_deleted,
    JSONExtractFloat(data, 'after', 'bas_price') AS bas_price,
    JSONExtractFloat(data, 'after', 'bas_standard_price') AS bas_standard_price,
    JSONExtractString(data, 'after', 'bas_currency') AS bas_currency,
    JSONExtractString(data, 'after', 'tag') AS tag,
    JSONExtractInt(data, 'after', 'shipment_completed') AS shipment_completed,
    JSONExtractInt(data, 'after', 'shipment_cancelled') AS shipment_cancelled,
    JSONExtractFloat(data, 'after', 'bas_standard_price_accuracy') AS bas_standard_price_accuracy,
    JSONExtractFloat(data, 'after', 'bas_standard_price_diff_from_selected_rate') AS bas_standard_price_diff_from_selected_rate,
    JSONExtractString(data, 'after', 'parent_rate_mode') AS parent_rate_mode
FROM brahmastra.kafka_fcl_freight_rate_statistics  
WHERE JSONExtractString(data,'op') in ('c','u');

CREATE TABLE brahmastra.fcl_freight_rate_statistics
(
        id UInt256,
        identifier FixedString(256),
        validity_id UUID,
        rate_id UUID,
        payment_term FixedString(256),
        schedule_type FixedString(256),
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
        origin_pricing_zone_map_id UUID,
        destination_pricing_zone_map_id UUID,
        price Float64,    
        standard_price Float64,     
        market_price Float64,
        validity_start Date,
        validity_end Date,
        currency FixedString(3),
        shipping_line_id UUID,
        service_provider_id UUID,
        mode FixedString(256),
        likes_count UInt16 DEFAULT 0,
        dislikes_count UInt16 DEFAULT 0,
        spot_search_count UInt16 DEFAULT 0,
        checkout_count UInt16 DEFAULT 0,
        bookings_created UInt16 DEFAULT 0,
        rate_created_at DateTime DEFAULT now(),
        rate_updated_at DateTime DEFAULT now(),
        validity_created_at DateTime DEFAULT now(),
        validity_updated_at DateTime DEFAULT now(),
        commodity FixedString(256),
        container_size String,
        container_type FixedString(256),
        containers_count UInt8 DEFAULT 0,
        origin_local_id UUID,
        destination_local_id UUID,
        applicable_origin_local_count UInt16 DEFAULT 0,
        applicable_destination_local_count UInt16 DEFAULT 0,
        origin_detention_id UUID,
        destination_detention_id UUID,
        origin_demurrage_id UUID,
        destination_demurrage_id UUID,
        cogo_entity_id UUID,
        rate_type FixedString(256),
        sourced_by_id UUID,
        procured_by_id UUID,
        revenue_desk_visit_count UInt16,
        so1_visit_count UInt16,
        created_at DateTime DEFAULT now(),
        updated_at DateTime DEFAULT now(),
        version UInt64 DEFAULT 1,
        sign Int8 DEFAULT 1,
        status FixedString(10) DEFAULT 'active',
        last_action FixedString(10) DEFAULT 'create',
        parent_rate_id UUID,
        parent_validity_id UUID,
        so1_select_count UInt16,
        parent_mode FixedString(255),
        source String,
        source_id UUID,
        performed_by_id UUID,
        performed_by_type FixedString(256),
        rate_sheet_id UUID,
        bulk_operation_id UUID,
        operation_created_at DateTime,
        operation_updated_at DateTime,
        is_deleted Bool DEFAULT false,
        bas_price Float64,
        bas_standard_price Float64,
        bas_currency FixedString(3),
        tag FixedString(256),
        shipment_completed UInt16,
        shipment_cancelled UInt16,
        bas_standard_price_accuracy Float64,
        bas_standard_price_diff_from_selected_rate Float64,
        parent_rate_mode String
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (is_deleted ,origin_continent_id,origin_country_id,origin_port_id,shipping_line_id,rate_id,validity_id)
ORDER BY (is_deleted, origin_continent_id,origin_country_id,origin_port_id,shipping_line_id,rate_id,validity_id, version, id);