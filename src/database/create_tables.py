from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_local_jobs import AirFreightRateLocalJob
from services.air_freight_rate.models.air_freight_rate_local_job_mappings import AirFreightRateLocalJobMapping
from services.fcl_freight_rate.models.fcl_freight_rate_local_jobs import FclFreightRateLocalJob
from services.fcl_freight_rate.models.fcl_freight_rate_local_job_mappings import FclFreightRateLocalJobMapping
from services.fcl_freight_rate.models.fcl_freight_rate_local_feedback import FclFreightRateLocalFeedback
from services.air_freight_rate.models.air_freight_rate_local_feedback import AirFreightRateLocalFeedback
from services.fcl_cfs_rate.models.fcl_cfs_rate_feedback import FclCfsRateFeedback
class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self, models):
        try:
            db.execute_sql(
                """
              CREATE SEQUENCE IF NOT EXISTS air_freight_rate_local_jobs_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;
              
              CREATE SEQUENCE IF NOT EXISTS fcl_freight_rate_local_jobs_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;

              CREATE SEQUENCE IF NOT EXISTS fcl_cfs_rate_feedback_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;
              
              CREATE SEQUENCE IF NOT EXISTS fcl_freight_rate_local_feedback_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;
              
              CREATE SEQUENCE IF NOT EXISTS air_freight_rate_local_feedback_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;

              ALTER TABLE fcl_freight_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE air_freight_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE haulage_freight_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE fcl_customs_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE air_customs_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE fcl_cfs_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE lcl_freight_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE ftl_freight_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE ltl_freight_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE lcl_customs_rate_job_mappings RENAME COLUMN shipment_serial_id TO source_serial_id;

              ALTER TABLE fcl_freight_rate_feedbacks DROP COLUMN preferred_detention_free_days;
              
              ALTER TABLE air_freight_rate_feedbacks DROP COLUMN preferred_storage_free_days;
              
              ALTER TABLE air_customs_rate_feedbacks ADD COLUMN if not exists spot_search_serial_id BIGINT;
              
              ALTER TABLE air_freight_rate_feedbacks ADD COLUMN if not exists spot_search_serial_id BIGINT;
              
              ALTER TABLE fcl_customs_rate_feedbacks ADD COLUMN if not exists spot_search_serial_id BIGINT;
              
              ALTER TABLE fcl_freight_rate_feedbacks ADD COLUMN if not exists spot_search_serial_id BIGINT;
              
              ALTER TABLE ftl_freight_rate_feedbacks ADD COLUMN if not exists spot_search_serial_id BIGINT;
              
              ALTER TABLE haulage_freight_rate_feedbacks ADD COLUMN if not exists spot_search_serial_id BIGINT;
              
              ALTER TABLE fcl_freight_rate_feedbacks ADD COLUMN if not exists preferred_free_days jsonb;
              
              ALTER TABLE air_customs_rate_feedbacks ADD COLUMN if not exists attachment_file_urls _text;
              
              ALTER TABLE air_freight_rate_feedbacks ADD COLUMN if not exists attachment_file_urls _text;
              
              ALTER TABLE fcl_customs_rate_feedbacks ADD COLUMN if not exists attachment_file_urls _text;
              
              ALTER TABLE fcl_freight_rate_feedbacks ADD COLUMN if not exists attachment_file_urls _text;
              
              ALTER TABLE ftl_freight_rate_feedbacks ADD COLUMN if not exists attachment_file_urls _text;
              
              ALTER TABLE haulage_freight_rate_feedbacks ADD COLUMN if not exists attachment_file_urls _text;"""
            )

            db.create_tables(models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = [
        AirFreightRateLocalJob,
        AirFreightRateLocalJobMapping,
        FclFreightRateLocalJob,
        FclFreightRateLocalJobMapping,
        FclFreightRateLocalFeedback,
        AirFreightRateLocalFeedback,
        FclCfsRateFeedback
    ]

    Table().create_tables(models)
