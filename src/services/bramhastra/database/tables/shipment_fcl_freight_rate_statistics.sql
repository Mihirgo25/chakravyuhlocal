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
ENGINE = file(CSV);