import re
from services.bramhastra.client import ClickHouse
from configs.definitions import ROOT_DIR
import os

class Sql():
    def __init__(self) -> None:
        self.root_path = f'{ROOT_DIR}/services/bramhastra/database/tables'

    def run(self,table_name: str):
        
        sql_file_path =  f'{self.root_path}/{table_name}.sql'
        
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
                