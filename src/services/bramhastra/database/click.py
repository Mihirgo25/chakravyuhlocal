import re
from services.bramhastra.client import ClickHouse
from configs.definitions import ROOT_DIR
import peewee


class Click:
    def __init__(self) -> None:
        self.root_path = f"{ROOT_DIR}/services/bramhastra/database/tables"

    def create(self, model: peewee.Model):
        sql_file_path = f"{self.root_path}/{model._meta.name}.sql"
        
        # check if sql_file_path exists

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
        model_cols = model._meta.field_names

        with open(sql_file_path, "r") as sql_file:
            sql_script = sql_file.read()
            column_names = re.findall(r"(?<=\n\s{4})(\w+)\s", sql_script)

        if column_names == model_cols:
            return True
        else:
            # columns missing , order missing
            print(f"columns not present {set(column_names) - set(model_cols)}")
            raise
        
        
    def create_tables(self,models):
        for model in models:
            self.create(model)
        
