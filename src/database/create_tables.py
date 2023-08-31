from database.db_session import db
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)
from services.bramhastra.models.worker_log import WorkerLog
from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic



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
    models = [
        FclFreightRateRequestStatistic,
        SpotSearchFclFreightRateStatistic,
        FeedbackFclFreightRateStatistic,
        ShipmentFclFreightRateStatistic,
        CheckoutFclFreightRateStatistic,
        WorkerLog,
    ]

    Table().create_tables(models)
