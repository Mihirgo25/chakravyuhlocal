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
from services.bramhastra.clickhouse.client import ClickHouse
from services.bramhastra.helpers.post_fcl_freight_helper import json_encoder_for_clickhouse
import peewee
    
class Send():
    def __init__(self) -> None:
        self.models = {
            # FclFreightRateRequestStatistic,
            # FeedbackFclFreightRateStatistic,
            # QuotationFclFreightRateStatistic,
            # ShipmentFclFreightRateStatistic,
            # SpotSearchFclFreightRateStatistic,
            FclFreightRateStatistic,
        }
        
    def build_query_and_insert_to_clickhouse(self,model: peewee.Model):
        self.client = ClickHouse().client
        
        data = json_encoder_for_clickhouse(list(model.select().dicts()))
        
        query = f"INSERT INTO brahmastra.{model._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 VALUES"
        
        columns = model._meta.fields
        
        values = []
    
        for  d in data:
            value = []
            for k,v in d.items():
                if v is None:
                    value.append('DEFAULT')
                elif isinstance(columns[k],peewee.UUIDField) or isinstance(columns[k],peewee.TextField) or isinstance(columns[k],peewee.CharField) or isinstance(columns[k],peewee.DateTimeField):
                    value.append(f"'{v}'")
                elif isinstance(columns[k],peewee.BooleanField):
                    value.append('true' if v else 'false')
                else:
                    value.append(f'{v}')
            values.append(f"({','.join(value)})")
            
        if values:
            self.client.execute(query + ','.join(values))
            model.delete().execute()
        
        
    def execute(self):
        for model in self.models:
            self.build_query_and_insert_to_clickhouse(model)
        
        
    