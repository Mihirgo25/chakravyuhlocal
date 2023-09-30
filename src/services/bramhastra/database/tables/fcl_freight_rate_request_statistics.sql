
CREATE TABLE brahmastra.kafka_fcl_freight_rate_request_statistics
(
    `data` String
)
ENGINE = Kafka('127.0.0.1:29092', 'arc.public.fcl_freight_rate_request_statistics', '001','JSONAsString')

CREATE MATERIALIZED VIEW brahmastra.fcl_freight_before_rate_request_statistics TO brahmastra.fcl_freight_rate_request_statistics
(
    `id` UInt256,
    `origin_port_id` UUID,
    `destination_port_id` UUID,
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
    `rate_request_id` UUID,
    `validity_ids` Array(String),
    `source` FixedString(256),
    `source_id` UUID,
    `performed_by_id` UUID,
    `performed_by_org_id` UUID,
    `importer_exporter_id` UUID,
    `closing_remarks` Array(String),
    `closed_by_id` UUID,
    `request_type` FixedString(256),
    `container_size` FixedString(256),
    `commodity` FixedString(256),
    `containers_count` UInt32,
    `is_rate_reverted` Bool DEFAULT true,
    `created_at` DateTime DEFAULT now(),
    `updated_at` DateTime DEFAULT now(),
    `sign` Int8 DEFAULT 1,
    `version` UInt32 DEFAULT 1,
    `operation_created_at` DateTime,
    `operation_updated_at` DateTime
) AS
SELECT
    JSONExtractUInt(data, 'before', 'id') AS id
    JSONExtractString(data, 'before', 'origin_port_id') AS origin_port_id
    JSONExtractString(data, 'before', 'destination_port_id') AS destination_port_id
    JSONExtractString(data, 'before', 'origin_region_id') AS origin_region_id
    JSONExtractString(data, 'before', 'destination_region_id') AS destination_region_id
    JSONExtractString(data, 'before', 'origin_country_id') AS origin_country_id
    JSONExtractString(data, 'before', 'destination_country_id') AS destination_country_id
    JSONExtractString(data, 'before', 'origin_continent_id') AS origin_continent_id
    JSONExtractString(data, 'before', 'destination_continent_id') AS destination_continent_id
    JSONExtractString(data, 'before', 'origin_trade_id') AS origin_trade_id
    JSONExtractString(data, 'before', 'destination_trade_id') AS destination_trade_id
    JSONExtractString(data, 'before', 'origin_pricing_zone_map_id') AS origin_pricing_zone_map_id
    JSONExtractString(data, 'before', 'destination_pricing_zone_map_id') AS destination_pricing_zone_map_id
    JSONExtractString(data, 'before', 'rate_request_id') AS rate_request_id
    JSONExtractArrayRaw(data, 'before', 'validity_ids') AS validity_ids
    JSONExtractString(data, 'before', 'source') AS source
    JSONExtractString(data, 'before', 'source_id') AS source_id
    JSONExtractString(data, 'before', 'performed_by_id') AS performed_by_id
    JSONExtractString(data, 'before', 'performed_by_org_id') AS performed_by_org_id
    JSONExtractString(data, 'before', 'importer_exporter_id') AS importer_exporter_id
    JSONExtractArrayRaw(data, 'before', 'closing_remarks') AS closing_remarks
    JSONExtractString(data, 'before', 'closed_by_id') AS closed_by_id
    JSONExtractString(data, 'before', 'request_type') AS request_type
    JSONExtractString(data, 'before', 'container_size') AS container_size
    JSONExtractString(data, 'before', 'commodity') AS commodity
    JSONExtractUInt(data, 'before', 'containers_count') AS containers_count
    JSONExtractBool(data, 'before', 'is_rate_reverted') AS is_rate_reverted
    parseDateTimeBestEffort(JSONExtractString(data, 'before', 'created_at')) AS created_at
    parseDateTimeBestEffort(JSONExtractString(data, 'before', 'updated_at')) AS updated_at
    JSONExtractInt(data, 'before', 'sign') AS sign
    JSONExtractUInt(data, 'before', 'version') AS version
    parseDateTimeBestEffort(JSONExtractString(data, 'before', 'operation_created_at')) AS operation_created_at
    parseDateTimeBestEffort(JSONExtractString(data, 'before', 'operation_updated_at')) AS operation_updated_at
    JSONExtractInt(data, 'source', 'lsn') AS version,
    -1 AS sign
    FROM brahmastra.kafka_fcl_freight_rate_request_statistics
    WHERE JSONExtract(data,'op','String') = 'u'

CREATE MATERIALIZED VIEW brahmastra.fcl_freight_after_rate_request_statistics TO brahmastra.fcl_freight_rate_request_statistics
(
    `id` UInt256,
    `origin_port_id` UUID,
    `destination_port_id` UUID,
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
    `rate_request_id` UUID,
    `validity_ids` Array(String),
    `source` FixedString(256),
    `source_id` UUID,
    `performed_by_id` UUID,
    `performed_by_org_id` UUID,
    `importer_exporter_id` UUID,
    `closing_remarks` Array(String),
    `closed_by_id` UUID,
    `request_type` FixedString(256),
    `container_size` FixedString(256),
    `commodity` FixedString(256),
    `containers_count` UInt32,
    `is_rate_reverted` Bool DEFAULT true,
    `created_at` DateTime DEFAULT now(),
    `updated_at` DateTime DEFAULT now(),
    `sign` Int8 DEFAULT 1,
    `version` UInt32 DEFAULT 1,
    `operation_created_at` DateTime,
    `operation_updated_at` DateTime
) AS
    SELECT
    JSONExtractUInt(data, 'after', 'id') AS id,
    JSONExtractString(data, 'after', 'origin_port_id') AS origin_port_id
    JSONExtractString(data, 'after', 'destination_port_id') AS destination_port_id
    JSONExtractString(data, 'after', 'origin_region_id') AS origin_region_id
    JSONExtractString(data, 'after', 'destination_region_id') AS destination_region_id
    JSONExtractString(data, 'after', 'origin_country_id') AS origin_country_id
    JSONExtractString(data, 'after', 'destination_country_id') AS destination_country_id
    JSONExtractString(data, 'after', 'origin_continent_id') AS origin_continent_id
    JSONExtractString(data, 'after', 'destination_continent_id') AS destination_continent_id
    JSONExtractString(data, 'after', 'origin_trade_id') AS origin_trade_id
    JSONExtractString(data, 'after', 'destination_trade_id') AS destination_trade_id
    JSONExtractString(data, 'after', 'origin_pricing_zone_map_id') AS origin_pricing_zone_map_id
    JSONExtractString(data, 'after', 'destination_pricing_zone_map_id') AS destination_pricing_zone_map_id
    JSONExtractString(data, 'after', 'rate_request_id') AS rate_request_id
    JSONExtractArrayRaw(data, 'after', 'validity_ids') AS validity_ids
    JSONExtractString(data, 'after', 'source') AS source
    JSONExtractString(data, 'after', 'source_id') AS source_id
    JSONExtractString(data, 'after', 'performed_by_id') AS performed_by_id
    JSONExtractString(data, 'after', 'performed_by_org_id') AS performed_by_org_id
    JSONExtractString(data, 'after', 'importer_exporter_id') AS importer_exporter_id
    JSONExtractArrayRaw(data, 'after', 'closing_remarks') AS closing_remarks
    JSONExtractString(data, 'after', 'closed_by_id') AS closed_by_id
    JSONExtractString(data, 'after', 'request_type') AS request_type
    JSONExtractString(data, 'after', 'container_size') AS container_size
    JSONExtractString(data, 'after', 'commodity') AS commodity
    JSONExtractUInt(data, 'after', 'containers_count') AS containers_count
    JSONExtractBool(data, 'after', 'is_rate_reverted') AS is_rate_reverted
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'created_at')) AS created_at
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'updated_at')) AS updated_at
    JSONExtractInt(data, 'after', 'sign') AS sign
    JSONExtractUInt(data, 'after', 'version') AS version
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'operation_created_at')) AS operation_created_at
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'operation_updated_at')) AS operation_updated_at
    JSONExtractFloat(data,'source','lsn') AS version,
    1 AS sign
FROM brahmastra.kafka_fcl_freight_rate_request_statistics  
WHERE JSONExtract(data,'op','String') in ('c','u')


CREATE TABLE brahmastra.fcl_freight_rate_request_statistics
(
    id UInt256,
    origin_port_id UUID,
    destination_port_id UUID,
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
    rate_request_id UUID,
    validity_ids Array(String),
    source FixedString(256),
    source_id UUID,
    performed_by_id UUID,
    performed_by_org_id UUID,
    importer_exporter_id UUID,
    closing_remarks Array(String),
    closed_by_id UUID,
    request_type FixedString(256),
    container_size FixedString(256),
    commodity FixedString(256),
    containers_count UInt32,
    is_rate_reverted Bool DEFAULT true,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
    operation_created_at DateTime,
    operation_updated_at DateTime
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_continent_id,origin_country_id,origin_port_id,performed_by_id)
ORDER BY (origin_continent_id,origin_country_id,origin_port_id,performed_by_id,updated_at);