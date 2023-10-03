
CREATE TABLE brahmastra.kafka_feedback_fcl_freight_rate_statistics
(
    `data` String
)
ENGINE = Kafka('127.0.0.1:29092', 'arc.public.feedback_fcl_freight_rate_statistics', '001','JSONAsString');

CREATE MATERIALIZED VIEW brahmastra.fcl_freight_before_feedback_rate_statistics TO brahmastra.feedback_fcl_freight_rate_statistics
(
    `id` UInt256,
    `fcl_freight_rate_statistic_id` UInt256,
    `feedback_id` UUID,
    `validity_id` UUID,
    `rate_id` UUID,
    `source` FixedString(256),
    `source_id` UUID,
    `performed_by_id` UUID,
    `performed_by_org_id` UUID,
    `created_at` DateTime DEFAULT now(),
    `updated_at` DateTime DEFAULT now(),
    `importer_exporter_id` UUID,
    `preferred_freight_rate` Float64 DEFAULT 0,
    `currency` FixedString(3),
    `feedbacks` Array(String),
    `closing_remarks` Array(String),
    `service_provider_id` UUID,
    `feedback_type` FixedString(256),
    `closed_by_id`  UUID,
    `status` FixedString(256),
    `serial_id` UInt256,
    `sign` Int8 DEFAULT 1,
    `version` UInt32 DEFAULT 1,
    `operation_created_at` DateTime DEFAULT now(),
    `operation_updated_at` DateTime DEFAULT now(),
    `is_rate_reverted` Bool
) AS
SELECT
    JSONExtractUInt(data, 'before', 'id') AS id,
    JSONExtractUInt(data, 'before', 'fcl_freight_rate_statistic_id') AS fcl_freight_rate_statistic_id,
    JSONExtractString(data, 'before', 'feedback_id') AS feedback_id,
    JSONExtractString(data, 'before', 'validity_id') AS validity_id,
    JSONExtractString(data, 'before', 'rate_id') AS rate_id,
    JSONExtractString(data, 'before', 'source') AS source,
    toUUIDOrZero(JSONExtractString(data, 'before', 'source_id')) AS source_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'performed_by_id')) AS performed_by_id,
    toUUIDOrZero(JSONExtractString(data, 'before', 'performed_by_org_id')) AS performed_by_org_id,
    parseDateTimeBestEffort(JSONExtractString(data, 'before', 'created_at')) AS created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'before', 'updated_at')) AS updated_at,
    toUUIDOrZero(JSONExtractString(data, 'before', 'importer_exporter_id')) AS importer_exporter_id,
    JSONExtractFloat(data, 'before', 'preferred_freight_rate') AS preferred_freight_rate,
    JSONExtractString(data, 'before', 'currency') AS currency,
    JSONExtractArrayRaw(data, 'before', 'feedbacks') AS feedbacks,
    JSONExtractArrayRaw(data, 'before', 'closing_remarks') AS closing_remarks,
    toUUIDOrZero(JSONExtractString(data, 'before', 'service_provider_id')) AS service_provider_id,
    JSONExtractString(data, 'before', 'feedback_type') AS feedback_type,
    toUUIDOrZero(JSONExtractString(data, 'before', 'closed_by_id')) AS closed_by_id,
    JSONExtractString(data, 'before', 'status') AS status,
    JSONExtractUInt(data, 'before', 'serial_id') AS serial_id,
    -1 AS sign,
    toUnixTimestamp64Milli(parseDateTime64BestEffort(visitParamExtractString(visitParamExtractRaw(data, 'before'), 'operation_updated_at'), 6)) AS version,
    parseDateTimeBestEffort(JSONExtractString(data, 'before', 'operation_created_at')) AS operation_created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'before', 'operation_updated_at')) AS operation_updated_at,
    JSONExtractBool(data, 'before', 'is_rate_reverted') AS is_rate_reverted
    FROM brahmastra.kafka_feedback_fcl_freight_rate_statistics
    WHERE JSONExtract(data,'op','String') = 'u';

CREATE MATERIALIZED VIEW brahmastra.fcl_freight_after_feedback_rate_statistics TO brahmastra.feedback_fcl_freight_rate_statistics
(
    `id` UInt256,
    `fcl_freight_rate_statistic_id` UInt256,
    `feedback_id` UUID,
    `validity_id` UUID,
    `rate_id` UUID,
    `source` FixedString(256),
    `source_id` UUID,
    `performed_by_id` UUID,
    `performed_by_org_id` UUID,
    `created_at` DateTime DEFAULT now(),
    `updated_at` DateTime DEFAULT now(),
    `importer_exporter_id` UUID,
    `preferred_freight_rate` Float64 DEFAULT 0,
    `currency` FixedString(3),
    `feedbacks` Array(String),
    `closing_remarks` Array(String),
    `service_provider_id` UUID,
    `feedback_type` FixedString(256),
    `closed_by_id`  UUID,
    `status` FixedString(256),
    `serial_id` UInt256,
    `sign` Int8 DEFAULT 1,
    `version` UInt32 DEFAULT 1,
    `operation_created_at` DateTime DEFAULT now(),
    `operation_updated_at` DateTime DEFAULT now(),
    `is_rate_reverted` Bool
) AS
    SELECT
    JSONExtractUInt(data, 'after', 'id') AS id,
    JSONExtractUInt(data, 'after', 'fcl_freight_rate_statistic_id') AS fcl_freight_rate_statistic_id,
    JSONExtractString(data, 'after', 'feedback_id') AS feedback_id,
    JSONExtractString(data, 'after', 'validity_id') AS validity_id,
    JSONExtractString(data, 'after', 'rate_id') AS rate_id,
    JSONExtractString(data, 'after', 'source') AS source,
    toUUIDOrZero(JSONExtractString(data, 'after', 'source_id')) AS source_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'performed_by_id')) AS performed_by_id,
    toUUIDOrZero(JSONExtractString(data, 'after', 'performed_by_org_id')) AS performed_by_org_id,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'created_at')) AS created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'updated_at')) AS updated_at,
    JSONExtractString(data, 'after', 'importer_exporter_id') AS importer_exporter_id,
    JSONExtractFloat(data, 'after', 'preferred_freight_rate') AS preferred_freight_rate,
    JSONExtractString(data, 'after', 'currency') AS currency,
    JSONExtractArrayRaw(data, 'after', 'feedbacks') AS feedbacks,
    JSONExtractArrayRaw(data, 'after', 'closing_remarks') AS closing_remarks,
    toUUIDOrZero(JSONExtractString(data, 'after', 'service_provider_id')) AS service_provider_id,
    JSONExtractString(data, 'after', 'feedback_type') AS feedback_type,
    toUUIDOrZero(JSONExtractString(data, 'after', 'closed_by_id')) AS closed_by_id,
    JSONExtractString(data, 'after', 'status') AS status,
    JSONExtractUInt(data, 'after', 'serial_id') AS serial_id,
    1 AS sign,
    toUnixTimestamp64Milli(parseDateTime64BestEffort(visitParamExtractString(visitParamExtractRaw(data, 'after'), 'operation_updated_at'), 6)) AS version,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'operation_created_at')) AS operation_created_at,
    parseDateTimeBestEffort(JSONExtractString(data, 'after', 'operation_updated_at')) AS operation_updated_at,
    JSONExtractBool(data, 'after', 'is_rate_reverted') AS is_rate_reverted
FROM brahmastra.kafka_feedback_fcl_freight_rate_statistics  
WHERE JSONExtract(data,'op','String') in ('c','u');


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
        service_provider_id UUID,
        feedback_type FixedString(256),
        closed_by_id  UUID,
        status FixedString(256),
        serial_id UInt256,
        sign Int8 DEFAULT 1,
        version UInt32 DEFAULT 1,
        operation_created_at DateTime DEFAULT now(),
        operation_updated_at DateTime DEFAULT now(),
        is_rate_reverted Bool
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
PRIMARY KEY (rate_id)
ORDER BY (rate_id,id, version);
