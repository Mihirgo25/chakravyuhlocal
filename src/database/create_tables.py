from database.db_session import db
from services.haulage_freight_rate.models.haulage_freight_rate_jobs import HaulageFreightRateJob
from services.haulage_freight_rate.models.haulage_freight_rate_job_mappings import HaulageFreightRateJobMapping
from services.fcl_customs_rate.models.fcl_customs_rate_jobs import FclCustomsRateJob
from services.fcl_customs_rate.models.fcl_customs_rate_job_mappings import FclCustomsRateJobMapping
 


class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self,models):
        try:
            db.execute_sql('CREATE SEQUENCE haulage_freight_rate_jobs_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;')
            db.execute_sql('CREATE SEQUENCE fcl_customs_rate_jobs_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;')
            db.create_tables(models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = [HaulageFreightRateJob, FclCustomsRateJob, HaulageFreightRateJobMapping, FclCustomsRateJobMapping]

    Table().create_tables(models)
