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
    standard_price Float64,     
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
    shipment_confirmed_by_importer_exporter_count UInt16 DEFAULT 0,
    shipment_in_progress_count UInt16 DEFAULT 0,
    shipment_received_count UInt16 DEFAULT 0,
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
    booking_rate_count UInt16 DEFAULT 0,
    parent_rate_id UUID,
    parent_validity_id UUID,
    source String,
    source_id UUID
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,origin_region_id,destination_region_id,origin_port_id,destination_port_id,rate_id,validity_id)
ORDER BY (origin_continent_id,destination_continent_id,origin_country_id,destination_country_id,origin_region_id,destination_region_id,origin_port_id,destination_port_id,rate_id,validity_id,rate_deviation_from_booking_rate);

CREATE TABLE brahmastra.stale_fcl_freight_rate_statistics
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
    destination_main_port_id UUID  ,
    origin_country_id UUID,
    destination_country_id UUID,
    origin_continent_id UUID,
    destination_continent_id UUID,
    origin_region_id UUID ,
    destination_region_id UUID,
    origin_trade_id UUID,
    destination_trade_id UUID ,
    origin_pricing_zone_map_id UUID  ,
    destination_pricing_zone_map_id UUID  ,
    price Float64,
    standard_price Float64,         
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
    shipment_confirmed_by_importer_exporter_count UInt16 DEFAULT 0,
    shipment_in_progress_count UInt16 DEFAULT 0,
    shipment_received_count UInt16 DEFAULT 0,
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
    booking_rate_count UInt16 DEFAULT 0,
    parent_rate_id UUID,
    parent_validity_id UUID,
    source String,
    source_id UUID,
)
ENGINE = File(CSV);