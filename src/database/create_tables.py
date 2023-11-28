from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_local_job import AirFreightRateLocalJob
from services.air_freight_rate.models.air_freight_rate_local_job_mapping import AirFreightRateLocalJobMapping
from services.fcl_freight_rate.models.fcl_freight_rate_local_job import FclFreightRateLocalJob
from services.fcl_freight_rate.models.fcl_freight_rate_local_job_mapping import FclFreightRateLocalJobMapping
from services.fcl_freight_rate.models.fcl_freight_rate_local_feedback import FclFreightRateLocalFeedback
from services.air_freight_rate.models.air_freight_rate_local_feedback import AirFreightRateLocalFeedback
from services.fcl_cfs_rate.models.fcl_cfs_rate_feedback import FclCfsRateFeedback
class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self, models):
        try:
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
