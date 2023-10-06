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
    origin_trade_id UUID,
    destination_trade_id UUID,
    origin_pricing_zone_map_id UUID,
    destination_pricing_zone_map_id UUID,
    price Float64,
    lower_limit Float64,
    upper_limit Float64,
    standard_price Float64,
    currency FixedString(3),
    validity_start Date,
    validity_end Date,
    density_category FixedString(256),
    max_density_weight Float64,
    min_density_weight Float64,
    airline_id UUID,
    service_provider_id UUID,
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
    commodity FixedString(256),
    commodity_type FixedString(256),
    commodity_sub_type FixedString(256),
    operation_type FixedString(256),
    shipment_type FixedString(256),
    stacking_type FixedString(256),
    origin_local_id UUID,
    destination_local_id UUID,
    surcharge_id UUID,
    cogo_entity_id UUID,
    price_type FixedString(256),
    rate_type FixedString(256),
    sourced_by_id UUID,
    procured_by_id UUID,
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
    parent_rate_id UUID,
    booking_rate_count UInt16 DEFAULT 0,
    parent_validity_id UUID,
    height Float64 DEFAULT 0,
    breadth Float64 DEFAULT 0,
    length Float64 DEFAULT 0,
    maximum_weight Float64 DEFAULT 0,
    flight_uuid UUID,
    discount_type FixedString(256),
    importer_exporter_id UUID,
    rate_not_available_entry Bool DEFAULT true,
    shipment_cargo_handed_over_at_origin_count UInt16,
    shipment_confirmed_by_importer_exporter_count UInt16 ,
    rate_deviation_from_cluster_base_rate Float64 DEFAULT 0,
    performed_by_id UUID,
    performed_by_type FixedString(256),
    operation_created_at DateTime,
    operation_updated_at DateTime,
    is_deleted Bool DEFAULT false
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (is_deleted,origin_continent_id,origin_country_id,origin_region_id,origin_airport_id,airline_id,rate_id,validity_id)
ORDER BY (is_deleted,origin_continent_id,origin_country_id,origin_region_id,origin_airport_id,airline_id,rate_id,validity_id,updated_at);

CREATE TABLE brahmastra.stale_air_freight_rate_statistics
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
    origin_trade_id UUID,
    destination_trade_id UUID,
    origin_pricing_zone_map_id UUID,
    destination_pricing_zone_map_id UUID,
    price Float64,
    lower_limit Float64,
    upper_limit Float64,
    standard_price Float64,
    currency FixedString(3),
    validity_start Date,
    validity_end Date,
    density_category FixedString(256),
    max_density_weight Float64,
    min_density_weight Float64,
    airline_id UUID,
    service_provider_id UUID,
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
    commodity FixedString(256),
    commodity_type FixedString(256),
    commodity_sub_type FixedString(256),
    operation_type FixedString(256),
    shipment_type FixedString(256),
    stacking_type FixedString(256),
    origin_local_id UUID,
    destination_local_id UUID,
    surcharge_id UUID,
    cogo_entity_id UUID,
    price_type FixedString(256),
    rate_type FixedString(256),
    sourced_by_id UUID,
    procured_by_id UUID,
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
    parent_rate_id UUID,
    booking_rate_count UInt16 DEFAULT 0,
    parent_validity_id UUID,
    height Float64 DEFAULT 0,
    breadth Float64 DEFAULT 0,
    length Float64 DEFAULT 0,
    maximum_weight Float64 DEFAULT 0,
    flight_uuid UUID,
    discount_type FixedString(256),
    importer_exporter_id UUID,
    rate_not_available_entry Bool DEFAULT true,
    shipment_cargo_handed_over_at_origin_count UInt16,
    shipment_confirmed_by_importer_exporter_count UInt16 ,
    rate_deviation_from_cluster_base_rate Float64 DEFAULT 0,
    performed_by_id UUID,
    performed_by_type FixedString(256),
    operation_created_at DateTime,
    operation_updated_at DateTime,
    is_deleted Bool DEFAULT false
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (is_deleted,origin_continent_id,origin_country_id,origin_region_id,origin_airport_id,airline_id,rate_id,validity_id)
ORDER BY (is_deleted,origin_continent_id,origin_country_id,origin_region_id,origin_airport_id,airline_id,rate_id,validity_id,updated_at);