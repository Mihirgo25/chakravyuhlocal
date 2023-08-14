CREATE TABLE brahmastra.feedback_fcl_freight_rate_statistics
(
    id UInt256,
    fcl_freight_rate_statistic_id UInt256,
    feedback_id UUID,
    validity_id UUID,
    rate_id UUID,
    source FixedString(256),
    source_id UUID,
    performed_by_id UUID,
    performed_by_org_id UUID,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    importer_exporter_id UUID,
    preferred_freight_rate Float64 DEFAULT 0,
    currency FixedString(3),
    feedbacks Array(String),
    closing_remarks Array(String),
    feedback_recieved_count UInt16 DEFAULT 0,
    service_provider_id UUID,
    feedback_type FixedString(256),
    closed_by_id  UUID,
    status FixedString(256),
    serial_id UInt256,
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id)
ORDER BY (rate_id,id);


CREATE TABLE brahmastra.stale_feedback_fcl_freight_rate_statistics
(
    id UInt256,
    fcl_freight_rate_statistic_id UInt256,
    feedback_id UUID,
    validity_id UUID,
    rate_id UUID,
    source FixedString(256),
    source_id UUID,
    performed_by_id UUID,
    performed_by_org_id UUID,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    importer_exporter_id UUID,
    preferred_freight_rate Float64 DEFAULT 0,
    currency FixedString(3),
    feedbacks Array(String),
    closing_remarks Array(String),
    feedback_recieved_count UInt16 DEFAULT 0,
    service_provider_id UUID,
    feedback_type FixedString(256),
    closed_by_id  UUID,
    status FixedString(256),
    serial_id UInt256,
    sign Int8 DEFAULT 1,
    version UInt32 DEFAULT 1,
)
ENGINE = File(CSV);

