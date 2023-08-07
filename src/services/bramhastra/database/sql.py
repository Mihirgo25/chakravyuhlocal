import re
from services.bramhastra.client import ClickHouse
from configs.definitions import ROOT_DIR
import os
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic
)
import peewee
class Sql():
    def __init__(self) -> None:
        self.root_path = f'{ROOT_DIR}/services/bramhastra/database/tables'

    def run(self,model: peewee.Model):
        
        sql_file_path =  f'{self.root_path}/{model._meta.name}.sql'
        
        clickhouse = ClickHouse()

        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()

        statements = re.split(r';\n', sql_script)

        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
            
            try:
                response = clickhouse.execute(statement)
                print(response)
            except Exception as e:
                print(e)
                
    def run_all(self):
        for filename in os.listdir(self.root_path):
            if filename.endswith(".sql"):
                self.run(filename)
                print(f'Done with {filename}')
    
    def is_valid_for_creation(self,model):
        table_name=model._meta.table_name
        model_cols=model._meta.field_names
        sql_file_path =  f'{self.root_path}/{table_name}.sql'
        
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
            column_names = re.findall(r'(?<=\n\s{4})(\w+)\s', sql_script)

        if column_names == model_cols:
            return True
        else:
            print(f'columns not present {set(column_names) - set(model_cols)}')
            raise
            

        