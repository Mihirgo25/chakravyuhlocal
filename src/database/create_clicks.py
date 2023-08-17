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
from services.bramhastra.database.dictionaries.country_rate_count import (
    CountryRateCount,
)
from database.create_tables import Table


class Clicks:
    def __init__(self, models=[], dictionaries=[]):
        self.models = models
        self.dictionaries = dictionaries

    def create(self):
        table = Table()
        click = Click()
        table.create_tables(self.models)
        click.create_tables(self.models)
        click.create_dictionaries(self.dictionaries)


if __name__ == "__main__":
    models = [
        FclFreightRateStatistic,
        FclFreightRateRequestStatistic,
        SpotSearchFclFreightRateStatistic,
        FeedbackFclFreightRateStatistic,
        ShipmentFclFreightRateStatistic,
        CheckoutFclFreightRateStatistic,
    ]
    dictionaries = [CountryRateCount]

    Clicks(models, dictionaries).create()
