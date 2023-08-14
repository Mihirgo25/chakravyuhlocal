import re
import os
from services.bramhastra.client import ClickHouse
from configs.definitions import ROOT_DIR
import peewee


class Click:
    def __init__(self) -> None:
        self.root_path = f"{ROOT_DIR}/services/bramhastra/database/tables"

    def create(self, model: peewee.Model):
        sql_file_path = f"{self.root_path}/{model._meta.table_name}.sql"
        if os.path.exists(sql_file_path):
            print(f"The file {sql_file_path} exists.")
        else:
            print(f"The file {sql_file_path} does not exist.")

        self.validate(sql_file_path, model)

        clickhouse = ClickHouse()

        with open(sql_file_path, "r") as sql_file:
            sql_script = sql_file.read()

        statements = re.split(r";\n", sql_script)

        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue

            try:
                response = clickhouse.execute(statement)
                print(response)
            except Exception as e:
                print(e)

    def validate(self, sql_file_path, model):
        model_cols = list(model._meta.fields.keys())

        with open(sql_file_path, "r") as sql_file:
            sql_script = sql_file.read()
            column_names = re.findall(r"(?<=\n\s{4})(\w+)\s", sql_script)

        missing_columns = set(model_cols) - set(column_names)
        ordered_match = len(missing_columns) == 0
        if ordered_match:
            return True
        else:
            print("Order Mismatched:")
            for i in range(len(model_cols)):
                if column_names[i] != model_cols[i]:
                    print(f"Expected: {model_cols[i]}, Found: {column_names[i]}")

        if missing_columns:
            print(f"Columns not present: {missing_columns}")

        raise Exception("Column Mismatch Detected")
        
        
    def create_tables(self,models):
        for model in models:
            self.create(model)
            
    def create_dictionaries(self, dictionaries):
        for dictionary in dictionaries:
            dictionary.create()

        
