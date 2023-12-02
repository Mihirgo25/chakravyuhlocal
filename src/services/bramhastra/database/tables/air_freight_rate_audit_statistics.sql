CREATE TABLE IF NOT EXISTS brahmastra.air_freight_rate_audit_statistics
(
    id UInt256,
    rate_id UUID,
    created_at DateTime,
    origin_continent_id UUID,
    destination_continent_id UUID,
    origin_country_id UUID,
    destination_country_id UUID,
    origin_airport_id UUID,
    destination_airport_id UUID,
    cogo_entity_id UUID,
    airline_id UUID,
    service_provider_id UUID,
    commodity FixedString(256),
    commodity_type FixedString(256),
    commodity_subtype FixedString(256),
    container_size FixedString(256),  
    container_type FixedString(256),  
    importer_exporter_id UUID,
    action_name FixedString(256),  
    performed_by_id UUID,
    performed_by_type FixedString(256),  
    currency FixedString(3),  
    code FixedString(256),  
    price Float32 DEFAULT 0,  
    market_price Float32 DEFAULT 0,  
    unit FixedString(256),  
    validity_start Date,  
    validity_end Date,  
    sourced_by_id UUID,
    procured_by_id UUID ,
    original_price Float32 DEFAULT 0,  
    standard_price Float32 DEFAULT 0 
)
ENGINE = MergeTree()
PRIMARY KEY (origin_continent_id,origin_country_id,origin_airport_id,airline_id)
ORDER BY (origin_continent_id,origin_country_id,origin_airport_id,airline_id,standard_price);
