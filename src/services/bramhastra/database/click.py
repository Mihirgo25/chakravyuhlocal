import re
import os
from services.bramhastra.client import ClickHouse
from configs.definitions import ROOT_DIR
import peewee

FILES_WITH_KAFKA = [
    "fcl_freight_actions.sql",
    "fcl_freight_rate_request_statistics.sql",
    "fcl_freight_rate_statistics_temp.sql",
    "feedback_fcl_freight_rate_statistics.sql",
    "air_freight_rate_request_statistics.sql",
    "feedback_air_freight_rate_statistics.sql",
    "air_freight_actions.sql",
    "air_freight_rate_audit_statistics.sql",
]


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
            regex = r"(?<=\n\s{4})(\w+)\s"
            if sql_file_path.split('/')[-1] in "".join(FILES_WITH_KAFKA):
                regex = r"(?<=\n\s{8})(\w+)\s"
            click_column_names_with_duplicates = re.findall(regex, sql_script)
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
            
            if 'sign' in missing_in_array1 and 'version' in missing_in_array1 and len(missing_in_array1):
                return

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


from services.bramhastra.models.air_freight_action import AirFreightAction
from services.bramhastra.models.air_freight_rate_audit_statistic import AirFreightRateAuditStatistic
from services.bramhastra.models.air_freight_rate_request_statistics import AirFreightRateRequestStatistic
from services.bramhastra.models.checkout_air_freight_rate_statistic import CheckoutAirFreightRateStatistic
from services.bramhastra.models.feedback_air_freight_rate_statistic import FeedbackAirFreightRateStatistic
from services.bramhastra.models.shipment_air_freight_rate_statistic import ShipmentAirFreightRateStatistic
from services.bramhastra.models.spot_search_air_freight_rate_statistic import SpotSearchAirFreightRateStatistic
models = [AirFreightRateRequestStatistic]
click = Click()
click.create_tables(models)