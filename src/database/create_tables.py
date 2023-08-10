from database.db_session import db
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
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

from services.bramhastra.database.click import Click


class Table:
    def __init__(self, models) -> None:
        self.models = models

    def create_tables(self):
        try:
            db.create_tables(self.models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise
        
        try:
            Click().create_tables(self.models)
        except Exception:
            pass    
        


if __name__ == "__main__":
    table = Table(
        [
            FclFreightRateStatistic,
            FclFreightRateRequestStatistic,
            SpotSearchFclFreightRateStatistic,
            FeedbackFclFreightRateStatistic,
            ShipmentFclFreightRateStatistic,
            CheckoutFclFreightRateStatistic,
        ]
    )
    table.create_tables()
