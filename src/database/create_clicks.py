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
    def __init__(self, models=[], dictionaries=[], ignore_oltp=False):
        self.models = models
        self.dictionaries = dictionaries
        self.ignore_oltp = ignore_oltp
        self.table = Table()
        self.click = Click()

    def create(self):
        if not self.ignore_oltp and self.models:
            self.table.create_tables(self.models)
        if self.models:
            self.click.create_tables(self.models)
        if self.dictionaries:
            self.click.create_dictionaries(self.dictionaries)
    
    def delete(self):
        for model in self.models:
            try:
                self.click.client.execute(f'drop table brahmastra.{model._meta.table_name}')
            except:
                print('Table does not exist:',model._meta.table_name)
            try:
                self.click.client.execute(f'drop table brahmastra.stale_{model._meta.table_name}')
            except:
                print('Table does not exist:',model._meta.table_name)
        self.click.drop_dictionaries(self.dictionaries)
        


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
