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

CREATE TABLE brahmastra.stale_checkout_fcl_freight_rate_statistics
(
    id UInt256,
    spot_search_id UUID,
    spot_search_fcl_customs_services_id UUID,
    checkout_id UUID,
    checkout_fcl_freight_rate_services_id UUID  ,
    validity_id UUID,
    rate_id UUID,
    sell_quotation_id UUID,
    buy_quotation_id UUID,
    shipment_id UUID  ,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    status FixedString(10) DEFAULT 'active',
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
)
ENGINE = file(CSV);