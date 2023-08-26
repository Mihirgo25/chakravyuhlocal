
CREATE TABLE brahmastra.air_freight_rate_statistics
(
    id UInt256,
    identifier FixedString(256),
    validity_id UUID,
    rate_id UUID,
    origin_airport_id UUID,
    destination_airport_id UUID,
    origin_country_id UUID,
    destination_country_id UUID,
    origin_continent_id UUID,
    destination_continent_id UUID,
    origin_region_id UUID,
    destination_region_id UUID,
    origin_trade_id UUID DEFAULT NULL,
    destination_trade_id UUID DEFAULT NULL,
    origin_pricing_zone_map_id UUID DEFAULT NULL,
    destination_pricing_zone_map_id UUID DEFAULT NULL,
    price Float64,
    lower_limit Float64,
    upper_limit Float64,
    currency FixedString(3),
    validity_start Date,
    validity_end Date,
    density_category FixedString(256),
    max_density_weight Float64,
    min_density_weight Float64,
    airline_id UUID DEFAULT NULL,
    service_provider_id UUID DEFAULT NULL,
    accuracy Float64 DEFAULT -1.0,
    source FixedString(256),
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
    commodity FixedString(256) DEFAULT NULL,
    commodity_type FixedString(256) DEFAULT NULL,
    commodity_sub_type FixedString(256) DEFAULT NULL,
    operation_type FixedString(256) DEFAULT NULL,
    shipment_type FixedString(256) DEFAULT NULL,
    stacking_type FixedString(256) DEFAULT NULL,
    origin_local_id UUID DEFAULT NULL,
    destination_local_id UUID DEFAULT NULL,
    surcharge_id UUID DEFAULT NULL,
    cogo_entity_id UUID DEFAULT NULL,
    price_type FixedString(256) DEFAULT NULL,
    rate_type FixedString(256),
    sourced_by_id UUID DEFAULT NULL,
    procured_by_id UUID DEFAULT NULL,
    shipment_aborted_count UInt16 DEFAULT 0,
    shipment_cancelled_count UInt16 DEFAULT 0,
    shipment_completed_count UInt16 DEFAULT 0,
    shipment_confirmed_by_service_provider_count UInt16 DEFAULT 0,
    shipment_awaited_service_provider_confirmation_count UInt16 DEFAULT 0,
    shipment_init_count UInt16 DEFAULT 0,
    shipment_flight_arrived_count UInt16 DEFAULT 0,
    shipment_flight_departed_count UInt16 DEFAULT 0,
    shipment_cargo_handed_over_at_destination_count UInt16 DEFAULT 0,
    shipment_is_active_count UInt16 DEFAULT 0,
    shipment_in_progress_count UInt16 DEFAULT 0,
    shipment_received_count UInt16 DEFAULT 0,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    version UInt32 DEFAULT 1,
    sign Int8 DEFAULT 1,
    revenue_desk_visit_count UInt16 DEFAULT 0,
    so1_visit_count UInt16 DEFAULT 0,
    status FixedString(10) DEFAULT 'active',
    last_action FixedString(10) DEFAULT 'create',
    rate_deviation_from_booking_rate Float32 DEFAULT 0,
    rate_deviation_from_booking_on_cluster_base_rate Float32 DEFAULT 0,
    rate_deviation_from_latest_booking Float32 DEFAULT 0,
    average_booking_rate Float64 DEFAULT -1,
    parent_rate_id UUID
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,origin_region_id,destination_region_id,origin_airport_id,destination_airport_id,rate_id,validity_id)
ORDER BY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,origin_region_id,destination_region_id,origin_airport_id,destination_airport_id,rate_id,validity_id,rate_deviation_from_booking_rate,updated_at);

CREATE TABLE brahmastra.feedback_air_freight_rate_statistics
(
    id UInt256,
    air_freight_rate_statistic_id UInt256,
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

CREATE TABLE brahmastra.quotation_air_freight_rate_statistics
(
    id UInt256,
    validity_id UUID,
    rate_id UUID,
    spot_search_id UUID,
    spot_search_air_customs_services_id UUID,
    checkout_id UUID,
    checkout_air_freight_rate_services_id UUID  ,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    shipment_id UUID  ,
    shipment_air_freight_rate_services_id UUID  ,
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


CREATE TABLE brahmastra.shipment_air_freight_rate_statistics
(
    id UInt256,
    spot_search_id UUID,
    spot_search_fcl_customs_services_id UUID,
    checkout_id UUID,
    checkout_air_freight_rate_services_id UUID  ,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    validity_id UUID,
    rate_id UUID,
    shipment_id UUID  ,
    shipment_air_freight_rate_services_id  UUID  ,
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

CREATE TABLE brahmastra.spot_search_air_freight_rate_statistics
(
    id UInt256,
    air_freight_rate_statistic_id UInt256,
    spot_search_id UUID,
    spot_search_air_freight_services_id UUID,
    checkout_id UUID,
    checkout_air_freight_rate_services_id UUID ,
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

CREATE TABLE brahmastra.air_freight_rate_request_statistics
(
    id UInt256,
    origin_airport_id UUID,
    destination_airport_id UUID,
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
