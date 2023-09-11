CREATE TABLE brahmastra.fcl_freight_rate_action
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
    commodity FixedString(256),
    container_size FixedString(256),
    container_type FixedString(256),
    shipping_line_id UUID,
    service_provider_id UUID,
    importer_exporter_id UUID,
    rate_id UUID,
    validity_id UUID,
    spot_search_id UUID,
    checkout_id UUID,
    checkout UInt32 DEFAULT 1
    shipment_id UUID,
    shipment UInt32 DEFAULT 1
    disliked UInt32 DEFAULT 1
    liked UInt32 DEFAULT 1
    feedback_id UUID,
    revenue_desk_visit UInt32 ,
    revenue_desk_select UInt32 ,
    so1_select UInt32 ,
    so1_selected_rate_id UUID,
    so1_selected_validity_id UUID,
    diff_from_selected_so1_rate Float64,
    fcl_freight_rate_statistic_id UUID,
    selected_fcl_freight_rate_statistic_id UUID,
    revenue_desk_visit UInt32 DEFAULT 1
    revenue_desk_select UInt32 DEFAULT 0
    given_priority UInt32 DEFAULT 0
    so1_visit UInt32 DEFAULT 1
    cancelled UInt32 DEFAULT 1
    completed UInt32 DEFAULT 1
    aborted UInt32 DEFAULT 1
    confirmed_by_importer_exporter UInt32 DEFAULT 1
    recieved UInt32 DEFAULT 0
    rate_request_id UUID,
    validity_id UUID,
    source FixedString(256),
    source_id UUID,
    importer_exporter_id  UUID,
    closing_remarks Array(UUID),
    closed_by_id  UUID,
    request_type FixedString(256),
    container_size FixedString(256),
    commodity FixedString(256),
    containers_count UInt32,
    is_rate_reverted Bool DEFAULT true,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
    operation_created_at DateTime DEFAULT now(),
    operation_updated_at DateTime DEFAULT now()
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_country_id, origin_port_id, shipping_line_id,rate_request_id,validity_id);
ORDER BY  (origin_country_id, origin_port_id, shipping_line_id,rate_request_id,validity_id);

CREATE TABLE brahmastra.stale_fcl_freight_rate_action
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
    commodity FixedString(256),
    container_size FixedString(256),
    container_type FixedString(256),
    shipping_line_id UUID,
    service_provider_id UUID,
    importer_exporter_id UUID,
    rate_id UUID,
    validity_id UUID,
    spot_search_id UUID,
    checkout_id UUID,
    checkout UInt32 DEFAULT 1
    shipment_id UUID,
    shipment UInt32 DEFAULT 1
    disliked UInt32 DEFAULT 1
    liked UInt32 DEFAULT 1
    feedback_id UUID,
    revenue_desk_visit UInt32 ,
    revenue_desk_select UInt32 ,
    so1_select UInt32 ,
    so1_selected_rate_id UUID,
    so1_selected_validity_id UUID,
    diff_from_selected_so1_rate Float64,
    fcl_freight_rate_statistic_id UUID,
    selected_fcl_freight_rate_statistic_id UUID,
    revenue_desk_visit UInt32 DEFAULT 1
    revenue_desk_select UInt32 DEFAULT 0
    given_priority UInt32 DEFAULT 0
    so1_visit UInt32 DEFAULT 1
    cancelled UInt32 DEFAULT 1
    completed UInt32 DEFAULT 1
    aborted UInt32 DEFAULT 1
    confirmed_by_importer_exporter UInt32 DEFAULT 1
    recieved UInt32 DEFAULT 0
    rate_request_id UUID,
    validity_id UUID,
    source FixedString(256),
    source_id UUID,
    importer_exporter_id  UUID,
    closing_remarks Array(UUID),
    closed_by_id  UUID,
    request_type FixedString(256),
    container_size FixedString(256),
    commodity FixedString(256),
    containers_count UInt32,
    is_rate_reverted Bool DEFAULT true,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
    operation_created_at DateTime DEFAULT now(),
    operation_updated_at DateTime DEFAULT now()
)

ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_country_id, origin_port_id, shipping_line_id,rate_request_id,validity_id);
ORDER BY  (origin_country_id, origin_port_id, shipping_line_id,rate_request_id,validity_id);