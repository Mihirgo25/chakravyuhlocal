CREATE TABLE brahmastra.checkout_air_freight_rate_statistics
(
    id UInt256,
    air_freight_rate_statistic_id Int256,
    source FixedString(256),
    source_id UUID,
    checkout_id UUID,
    checkout_air_freight_rate_services_id UUID,
    validity_id UUID,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    rate_id UUID,
    currency FixedString(3),
    importer_exporter_id UUID,
    shipment_id UUID,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    total_buy_price UInt16,
    status FixedString(10) DEFAULT 'active',
    sign Int8 DEFAULT 1,
    version UInt64 DEFAULT 1,
    c_at DateTime DEFAULT now(),
    u_at DateTime DEFAULT now()
)

ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id,validity_id,checkout_id)
ORDER BY (rate_id,validity_id,checkout_id,id);

CREATE TABLE brahmastra.stale_checkout_air_freight_rate_statistics
(
    id UInt256,
    air_freight_rate_statistic_id Int256,
    source FixedString(256),
    source_id UUID,
    checkout_id UUID,
    checkout_air_freight_rate_services_id UUID,
    validity_id UUID,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    rate_id UUID,
    currency FixedString(3),
    importer_exporter_id UUID,
    shipment_id UUID,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    total_buy_price UInt16,
    status FixedString(10) DEFAULT 'active',
    sign Int8 DEFAULT 1,
    version UInt64 DEFAULT 1,
    c_at DateTime DEFAULT now(),
    u_at DateTime DEFAULT now()
)
ENGINE = File(CSV);