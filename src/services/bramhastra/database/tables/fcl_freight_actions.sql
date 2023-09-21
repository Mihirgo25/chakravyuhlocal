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
    checkout_created_at DateTime,
    checkout_fcl_freight_service_id UUID,
    checkout UInt8,
    shipment UInt8,
    shipment_id UUID,
    shipment_serial_id UInt256,
    shipment_source String,
    containers_count UInt8,
    cargo_weight_per_container Float64,
    shipment_state String,
    shipment_service_id UUID,
    shipment_cancelled UInt8,
    shipment_cancellation_reason String,
    shipment_completed UInt8,
    shipment_aborted UInt8,
    shipment_in_progress UInt8,
    shipment_confirmed_by_importer_exporter UInt8,
    shipment_recieved UInt8,
    shipment_source_id UUID,
    shipment_created_at DateTime,
    shipment_updated_at DateTime,
    shipment_service_state String,
    shipment_service_is_active String,
    shipment_service_created_at DateTime,
    shipment_service_updated_at DateTime,
    shipment_service_cancellation_reason String,
    disliked UInt8,
    liked UInt8,
    rate_request_ids Array(UUID),
    feedback_ids Array(UUID),
    so1_select INT,
    selected_bas_standard_price Float64 DEFAULT 0,
    bas_standard_price_accuracy Float64 DEFAULT 0,
    bas_standard_price_diff_from_selected_rate Float64 DEFAULT 0,
    selected_fcl_freight_rate_statistic_id UInt256,
    selected_rate_id UUID,
    selected_validity_id UUID,
    revenue_desk_visit UInt8,
    revenue_desk_select UInt8,
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