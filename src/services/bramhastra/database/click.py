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
            column_names_with_duplicates = re.findall(r"(?<=\n\s{4})(\w+)\s", sql_script)
            column_names_set = set()
            column_names = []
            for name in column_names_with_duplicates:
                if name not in column_names_set:
                    column_names_set.add(name)
                    column_names.append(name)
    
        if(len(model_cols)!=len(column_names)):
            raise Exception("\nColumn length mismatched !!")
        
        missing_columns = []
        for idx, name in enumerate(model_cols):
            if(column_names[idx] != name):
                missing_columns.append(name)
        
        if len(missing_columns) > 0:
            print('!! Columns missing:')
            for column in missing_columns:
                print(column)

            raise Exception("\nColumn names order mismatched !!")

        return True        
        
    def create_tables(self,models):
        for model in models:
            self.create(model)

    def create_dictionaries(self, dictionaries):
        for dictionary in dictionaries:
            dictionary().create()
