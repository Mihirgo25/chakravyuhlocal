CREATE TABLE brahmastra.shipment_fcl_freight_rate_statistics
(
    id UInt256,
    fcl_freight_rate_statistic_id UInt256,
    rate_id UUID,
    validity_id UUID,
    shipment_id UUID,
    shipment_fcl_freight_service_id UUID,
    service_state String,
    service_is_active Bool,
    service_cancellation_reason String,
    service_created_at DateTime DEFAULT now(),
    service_updated_at DateTime DEFAULT now(),
    shipping_line_id UUID,
    service_provider_id UUID,
    serial_id UInt256,
    importer_exporter_id UUID,
    shipment_type FixedString(256),
    services Array(FixedString(256)),
    source FixedString(256),
    source_id UUID,
    state FixedString(256),
    cancellation_reason String,
    buy_quotation_id UUID,
    buy_quotation_created_at DateTime DEFAULT now(),
    buy_quotation_updated_at DateTime DEFAULT now(),
    is_deleted Bool,
    total_price Float32,
    total_price_discounted Float32,
    tax_price Float32,
    tax_price_discounted Float32,
    tax_total_price Float32,
    tax_total_price_discounted Float32,
    currency FixedString(3),
    standard_total_price Float32,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    sign Int8 DEFAULT 1,
    version UInt64 DEFAULT 1
)

ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id)
ORDER BY (rate_id,id);


CREATE TABLE brahmastra.stale_shipment_fcl_freight_rate_statistics
(
    id UInt256,
    fcl_freight_rate_statistic_id UInt256,
    rate_id UUID,
    validity_id UUID,
    shipment_id UUID,
    shipment_fcl_freight_service_id UUID,
    service_state String,
    service_is_active Bool,
    service_cancellation_reason String,
    service_created_at DateTime DEFAULT now(),
    service_updated_at DateTime DEFAULT now(),
    shipping_line_id UUID,
    service_provider_id UUID,
    serial_id UInt256,
    importer_exporter_id UUID,
    shipment_type FixedString(256),
    services Array(FixedString(256)),
    source FixedString(256),
    source_id UUID,
    state FixedString(256),
    cancellation_reason String,
    buy_quotation_id UUID,
    buy_quotation_created_at DateTime DEFAULT now(),
    buy_quotation_updated_at DateTime DEFAULT now(),
    is_deleted Bool,
    total_price Float32,
    total_price_discounted Float32,
    tax_price Float32,
    tax_price_discounted Float32,
    tax_total_price Float32,
    tax_total_price_discounted Float32,
    currency FixedString(3),
    standard_total_price Float32,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    sign Int8 DEFAULT 1,
    version UInt64 DEFAULT 1
)
ENGINE = File(CSV);