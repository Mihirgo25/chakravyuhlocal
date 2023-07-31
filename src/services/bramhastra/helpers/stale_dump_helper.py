from services.bramhastra.clickhouse.connect import get_clickhouse_client
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from services.bramhastra.models.quotation_fcl_freight_rate_statistic import (
    QuotationFclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)

class StaleDump:
    def __init__(self) -> None:
        self.clickhouse = get_clickhouse_client()
        self.models = [FclFreightRateStatistic]
    
    def send_data_to_stale_tables(self,model):
        query = f"INSERT INTO brahmastra.stale_{model._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT * FROM brahmastra.{model._meta.table_name}"
        self.clickhouse.execute(query)
        self.clickhouse.execute(f"OPTIMIZE TABLE brahmastra.{model._meta.table_name}")
    
    def execute(self):
        for model in self.models:
            self.send_data_to_stale_tables(model)
        
                
    
            