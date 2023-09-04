from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJobs
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobsMapping
from services.fcl_freight_rate.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJobs


class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self,models):
        try:
            db.create_tables(models)
            db.execute_sql('CREATE SEQUENCE air_freight_rate_jobs_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;')
            db.execute_sql('CREATE SEQUENCE fcl_freight_rate_jobs_serial_id_seq START WITH 1 INCREMENT BY 1 MINVALUE 0;')
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = [AirFreightRateJobs, AirFreightRateJobsMapping, FclFreightRateJobsMapping, FclFreightRateJobs]

    Table().create_tables(models)
