import re
import os
from services.bramhastra.client import ClickHouse
from configs.definitions import ROOT_DIR
import peewee


class Click:
    def __init__(self) -> None:
        self.root_path = f"{ROOT_DIR}/services/bramhastra/database/tables"
        self.client = ClickHouse()

    def create(self, model: peewee.Model):
        sql_file_path = f"{self.root_path}/{model._meta.table_name}.sql"
        if not os.path.exists(sql_file_path):
            raise ValueError(f"The file {sql_file_path} does not exist.")

        self.validate(sql_file_path, model)

        with open(sql_file_path, "r") as sql_file:
            sql_script = sql_file.read()

        statements = re.split(r";\n", sql_script)

        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue

            try:
                self.client.execute(statement)
            except Exception as e:
                print(e)

    def validate(self, sql_file_path, model):
        model_column_names = list(model._meta.fields.keys())

        with open(sql_file_path, "r") as sql_file:
            sql_script = sql_file.read()
            click_column_names_with_duplicates = re.findall(
                r"(?<=\n\s{4})(\w+)\s", sql_script
            )
            click_column_names_set = set()
            click_column_names = []
            for name in click_column_names_with_duplicates:
                if name not in click_column_names_set:
                    click_column_names_set.add(name)
                    click_column_names.append(name)

        self.compare_arrays(model_column_names, click_column_names)

        return True

    def compare_arrays(self, model_columns, click_columns):
        if len(set(model_columns)) != len(model_columns) or len(
            set(click_columns)
        ) != len(click_columns):
            duplicates_in_array1 = [
                item for item in model_columns if model_columns.count(item) > 1
            ]
            duplicates_in_array2 = [
                item for item in click_columns if click_columns.count(item) > 1
            ]

            message = "Arrays should have unique elements"
            if duplicates_in_array1:
                message += (
                    f"\nDuplicate values in Model: {', '.join(duplicates_in_array1)}"
                )
            if duplicates_in_array2:
                message += (
                    f"\nDuplicate values in Click: {', '.join(duplicates_in_array2)}"
                )

            raise ValueError(message)

        if model_columns != click_columns:
            missing_in_array1 = [
                item for item in click_columns if item not in model_columns
            ]
            missing_in_array2 = [
                item for item in model_columns if item not in click_columns
            ]

            message = "Arrays do not match exactly"
            if missing_in_array1:
                message += f"\nMissing in Model: {', '.join(missing_in_array1)}"
            if missing_in_array2:
                message += f"\nMissing in Click: {', '.join(missing_in_array2)}"

            raise ValueError(message)

        return

    def create_tables(self, models):
        for model in models:
            self.create(model)

    def create_dictionaries(self, dictionaries):
        for dictionary in dictionaries:
            dictionary().create()

    def drop_dictionaries(self, dictionaries):
        for dictionary in dictionaries:
            dictionary().drop()
