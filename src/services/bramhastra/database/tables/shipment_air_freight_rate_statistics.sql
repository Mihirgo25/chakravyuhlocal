CREATE TABLE brahmastra.shipment_air_freight_rate_statistics
(
    id UInt256,
    air_freight_rate_statistic_id UInt256,
    rate_id UUID,
    validity_id UUID,
    shipment_id UUID,
    shipment_serial_id UInt256,
    shipment_source FixedString(256),
    containers_count Int32,
    cargo_weight_per_container Float32,
    shipment_state FixedString(256),
    shipment_service_id UUID,
    shipment_cancelled Int32,
    shipment_cancellation_reason String,
    shipment_completed Int32,
    shipment_aborted Int32,
    shipment_in_progress Int32,
    shipment_confirmed_by_importer_exporter Int32,
    shipment_recieved Int32,
    shipment_source_id UUID,
    shipment_created_at DateTime DEFAULT now(),
    shipment_updated_at DateTime DEFAULT now(),
    shipment_service_state FixedString(256),
    shipment_service_is_active FixedString(256),
    shipment_service_created_at DateTime DEFAULT now(),
    shipment_service_updated_at DateTime DEFAULT now(),
    shipment_service_cancellation_reason  FixedString(256),
    sign Int8 DEFAULT 1,
    version UInt64 DEFAULT 1,
    operation_created_at DateTime DEFAULT now(),
    operation_updated_at DateTime DEFAULT now()
)

ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (id)
ORDER BY (rate_id,id);


CREATE TABLE brahmastra.stale_shipment_air_freight_rate_statistics
(
    id UInt256,
    air_freight_rate_statistic_id UInt256,
    rate_id UUID,
    validity_id UUID,
    shipment_id UUID,
    shipment_serial_id UInt256,
    shipment_source FixedString(256),
    containers_count Int32,
    cargo_weight_per_container Float32,
    shipment_state FixedString(256),
    shipment_service_id UUID,
    shipment_cancelled Int32,
    shipment_cancellation_reason String,
    shipment_completed Int32,
    shipment_aborted Int32,
    shipment_in_progress Int32,
    shipment_confirmed_by_importer_exporter Int32,
    shipment_recieved Int32,
    shipment_source_id UUID,
    shipment_created_at DateTime DEFAULT now(),
    shipment_updated_at DateTime DEFAULT now(),
    shipment_service_state FixedString(256),
    shipment_service_is_active FixedString(256),
    shipment_service_created_at DateTime DEFAULT now(),
    shipment_service_updated_at DateTime DEFAULT now(),
    shipment_service_cancellation_reason  FixedString(256),
    sign Int8 DEFAULT 1,
    version UInt64 DEFAULT 1,
    operation_created_at DateTime DEFAULT now(),
    operation_updated_at DateTime DEFAULT now()
)
ENGINE = File(CSV);