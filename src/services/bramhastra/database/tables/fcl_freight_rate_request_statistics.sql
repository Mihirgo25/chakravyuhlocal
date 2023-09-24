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