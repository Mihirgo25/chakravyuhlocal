CREATE DATABASE IF NOT EXISTS brahmastra;

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
    origin_main_port_id UUID  ,
    destination_main_port_id UUID ,
    origin_region_id UUID ,
    destination_region_id UUID,
    origin_country_id UUID,
    destination_country_id UUID,
    origin_continent_id UUID,
    destination_continent_id UUID,
    origin_trade_id UUID,
    destination_trade_id UUID ,
    origin_pricing_zone_map_id UUID  ,
    destination_pricing_zone_map_id UUID  ,
    price Float64,         
    market_price Float64,
    validity_start Date,
    validity_end Date,
    currency FixedString(3),
    shipping_line_id UUID  ,
    service_provider_id UUID  ,
    accuracy Float64 DEFAULT -1.0,
    mode FixedString(256),
    likes_count UInt16 DEFAULT 0,
    dislikes_count UInt16 DEFAULT 0,
    feedback_recieved_count UInt16 DEFAULT 0,
    dislikes_rate_reverted_count UInt16 DEFAULT 0,
    spot_search_count UInt16 DEFAULT 0,
    buy_quotations_created UInt16 DEFAULT 0,
    sell_quotations_created UInt16 DEFAULT 0,
    checkout_count UInt16 DEFAULT 0,
    bookings_created UInt16 DEFAULT 0,
    rate_created_at DateTime DEFAULT now(),
    rate_updated_at DateTime DEFAULT now(),
    validity_created_at DateTime DEFAULT now(),
    validity_updated_at DateTime DEFAULT now(),
    commodity FixedString(256),
    container_size FixedString(10),
    container_type FixedString(256),
    containers_count UInt8 DEFAULT 0,
    origin_local_id UUID  ,
    destination_local_id UUID  ,
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
    shipment_aborted_count UInt16 DEFAULT 0,
    shipment_cancelled_count UInt16 DEFAULT 0,
    shipment_completed_count UInt16 DEFAULT 0,
    shipment_confirmed_by_service_provider_count UInt16 DEFAULT 0,
    shipment_in_progress_count UInt16 DEFAULT 0,
    shipment_recieved_count UInt16 DEFAULT 0,
    shipment_awaited_service_provider_confirmation_count UInt16 DEFAULT 0,
    shipment_init_count UInt16 DEFAULT 0,
    shipment_containers_gated_in_count UInt16 DEFAULT 0,
    shipment_containers_gated_out_count UInt16 DEFAULT 0,
    shipment_vessel_arrived_count UInt16 DEFAULT 0,
    shipment_is_active_count UInt16 DEFAULT 0,
    shipment_cancellation_reason_got_a_cheaper_rate_from_my_service_provider_count UInt16 DEFAULT 0,
    shipment_booking_rate_is_too_low_count UInt16 DEFAULT 0,
    revenue_desk_visit_count UInt16 DEFAULT 0,
    so1_visit_count UInt16 DEFAULT 0,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    version UInt32 DEFAULT 1,
    sign Int8 DEFAULT 1,
    status FixedString(10) DEFAULT 'active',
    last_action FixedString(10) DEFAULT 'create',
    rate_deviation_from_booking_rate Float32 DEFAULT 0,
    rate_deviation_from_cluster_base_rate Float32 DEFAULT 0,
    rate_deviation_from_booking_on_cluster_base_rate Float32 DEFAULT 0,
    rate_deviation_from_latest_booking Float32 DEFAULT 0,
    rate_deviation_from_reverted_rate Float64 DEFAULT 0,
    average_booking_rate Float64 DEFAULT -1,
    parent_rate_id UUID,
    source String,
    source_id UUID
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,origin_region_id,destination_region_id,origin_port_id,destination_port_id,rate_id,validity_id)
ORDER BY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,origin_region_id,destination_region_id,origin_port_id,destination_port_id,rate_id,validity_id,rate_deviation_from_booking_rate);


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
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,origin_region_id,destination_region_id,origin_port_id,destination_port_id)
ORDER BY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,origin_region_id,destination_region_id,origin_port_id,destination_port_id,updated_at);

CREATE TABLE brahmastra.checkout_fcl_freight_rate_statistics
(
    id UInt256,
    fcl_freight_rate_statistic_id UUID,
    source FixedString(256),
    source_id UUID,
    checkout_id UUID,
    checkout_fcl_freight_rate_services_id UUID  ,
    validity_id UUID,
    rate_id UUID,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    shipment_id UUID ,
    total_buy_price UInt16,
    importer_exporter_id UUID,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    status FixedString(10) DEFAULT 'active',
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
    c_at DateTime DEFAULT now(),
    d_at DateTime DEFAULT now()
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id,checkout_id,validity_id)
ORDER BY (rate_id,checkout_id,validity_id,id);

CREATE TABLE brahmastra.feedback_fcl_freight_rate_statistics
(
    id UInt256,
    fcl_freight_rate_statistic_id UInt256,
    feedback_id UUID,
    validity_id UUID,
    rate_id UUID,
    source FixedString(256),
    source_id UUID  ,
    performed_by_id UUID  ,
    performed_by_org_id UUID  ,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    importer_exporter_id UUID ,
    feedbacks Array(String),
    closing_remarks Array(String),
    feedback_recieved_count UInt16 DEFAULT 0,
    service_provider_id UUID ,
    feedback_type FixedString(256),
    closed_by_id  UUID,
    status FixedString(256),
    serial_id UInt256,
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id)
ORDER BY (rate_id,version);

CREATE TABLE brahmastra.quotation_fcl_freight_rate_statistics
(
    id UInt256,
    validity_id UUID,
    rate_id UUID,
    spot_search_id UUID,
    spot_search_fcl_customs_services_id UUID,
    checkout_id UUID,
    checkout_fcl_freight_rate_services_id UUID  ,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    shipment_id UUID  ,
    shipment_fcl_freight_rate_services_id UUID  ,
    cancellation_reason String,
    is_active Bool,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    status FixedString(10) DEFAULT 'active',
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id)
ORDER BY (rate_id,version);


CREATE TABLE brahmastra.shipment_fcl_freight_rate_services_statistics
(
    id UInt256,
    spot_search_id UUID,
    spot_search_fcl_customs_services_id UUID,
    checkout_id UUID,
    checkout_fcl_freight_rate_services_id UUID  ,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    validity_id UUID,
    rate_id UUID,
    shipment_id UUID  ,
    shipment_fcl_freight_rate_services_id  UUID  ,
    cancellation_reason String,
    is_active Bool,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    status FixedString(10) DEFAULT 'active',
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id)
ORDER BY (rate_id,version);

CREATE TABLE brahmastra.spot_search_fcl_freight_rate_statistics
(
    id UInt256,
    fcl_freight_rate_statistic_id UInt256,
    spot_search_id UUID,
    spot_search_fcl_freight_services_id UUID,
    checkout_id UUID,
    checkout_fcl_freight_rate_services_id UUID ,
    validity_id UUID,
    rate_id UUID,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    shipment_id UUID,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id)
ORDER BY (rate_id,version);

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
    destination_trade_id  UUID,
    origin_pricing_zone_map_id  UUID,
    destination_pricing_zone_map_id  UUID,
    rate_request_id  UUID,
    validity_ids  Array(String),
    source  FixedString(256),
    source_id  UUID,
    performed_by_id  UUID,
    performed_by_org_id  UUID,
    importer_exporter_id  UUID,
    closing_remarks  Array(String),
    closed_by_id  UUID,
    request_type  FixedString(256),
    container_size  FixedString(256),
    commodity  FixedString(256),
    containers_count  Int8,
    is_rate_reverted  Bool,
    created_at  DateTime DEFAULT now(),
    updated_at  DateTime DEFAULT now(),
    sign  Int8 DEFAULT 1,
    version Int8 DEFAULT 1
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,version)
ORDER BY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,version);
