from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from services.air_freight_rate.models.air_freight_rate_jobs_mapping import AirFreightRateJobMapping
from services.fcl_freight_rate.models.fcl_freight_rate_job_mappings import FclFreightRateJobMapping
from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from services.fcl_freight_rate.models.critical_port_trend_indexes import CriticalPortTrendIndex

class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self,models):
        try:
            db.create_tables(models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = [AirFreightRateJob, AirFreightRateJobMapping, FclFreightRateJobMapping, FclFreightRateJob, CriticalPortTrendIndex]

    Table().create_tables(models)
