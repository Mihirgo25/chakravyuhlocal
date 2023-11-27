from peewee import *
from playhouse.postgres_ext import *
from services.bramhastra.enums import Fcl
from services.bramhastra.client import ClickHouse
from micro_services.client import common
from services.bramhastra.models.fcl_freight_rate_audit_statistic import (
    FclFreightRateAuditStatistic,
)
from database.create_clicks import Clicks
from datetime import datetime, timezone
from services.bramhastra.client import ClickHouse
from services.bramhastra.models.fcl_freight_rate_audit_statistic import (
    FclFreightRateAuditStatistic,
)
from configs.env import *
from fastapi.encoders import jsonable_encoder
from datetime import datetime


def json_encoder(data):
    return jsonable_encoder(
        data, custom_encoder={datetime: lambda dt: dt.isoformat() + "Z"}
    )


database = PostgresqlDatabase(
    RAILS_DATABASE_NAME,
    **{
        "host": RAILS_DATABASE_HOST,
        "port": RAILS_DATABASE_PORT,
        "user": RAILS_DATABASE_USER,
        "password": RAILS_DATABASE_PASSWORD,
    },
)


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = database


class FclFreightRateAudit(BaseModel):
    action_name = CharField(null=True)
    bulk_operation_id = UUIDField(index=True, null=True)
    created_at = DateTimeField()
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], unique=True)
    object_id = UUIDField(null=True)
    object_type = CharField(null=True)
    performed_by_id = UUIDField(null=True)
    procured_by_id = UUIDField(null=True)
    rate_sheet_id = UUIDField(index=True, null=True)
    source = CharField(null=True)
    sourced_by_id = UUIDField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = "fcl_freight_rate_audits"
        indexes = ((("object_type", "object_id"), False),)
        primary_key = False


class FclFreightRate(BaseModel):
    cogo_entity_id = UUIDField(index=True, null=True)
    commodity = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField()
    destination_continent_id = UUIDField(index=True, null=True)
    destination_country_id = UUIDField(index=True, null=True)
    destination_demurrage_id = UUIDField(null=True)
    destination_detention_id = UUIDField(null=True)
    destination_local = BinaryJSONField(null=True)
    destination_local_id = UUIDField(index=True, null=True)
    destination_local_line_items_error_messages = BinaryJSONField(
        constraints=[SQL("DEFAULT '{}'::jsonb")], null=True
    )
    destination_local_line_items_info_messages = BinaryJSONField(
        constraints=[SQL("DEFAULT '{}'::jsonb")], null=True
    )
    destination_location_ids = ArrayField(
        constraints=[SQL("DEFAULT '{}'::uuid[]")],
        field_class=UUIDField,
        index=True,
        null=True,
    )
    destination_main_port_id = UUIDField(null=True)
    destination_plugin_id = UUIDField(index=True, null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_trade_id = UUIDField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], unique=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporters_count = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_destination_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_destination_detention_slabs_missing = BooleanField(index=True, null=True)
    is_destination_local_line_items_error_messages_present = BooleanField(
        index=True, null=True
    )
    is_destination_local_line_items_info_messages_present = BooleanField(
        index=True, null=True
    )
    is_destination_plugin_slabs_missing = BooleanField(index=True, null=True)
    is_origin_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_origin_detention_slabs_missing = BooleanField(index=True, null=True)
    is_origin_local_line_items_error_messages_present = BooleanField(
        index=True, null=True
    )
    is_origin_local_line_items_info_messages_present = BooleanField(
        index=True, null=True
    )
    is_origin_plugin_slabs_missing = BooleanField(index=True, null=True)
    is_weight_limit_slabs_missing = BooleanField(null=True)
    last_rate_available_date = DateField(null=True)
    omp_dmp_sl_sp = CharField(null=True)
    origin_continent_id = UUIDField(index=True, null=True)
    origin_country_id = UUIDField(index=True, null=True)
    origin_detention_id = UUIDField(null=True)
    origin_local = BinaryJSONField(null=True)
    origin_local_id = UUIDField(index=True, null=True)
    origin_local_line_items_error_messages = BinaryJSONField(
        constraints=[SQL("DEFAULT '{}'::jsonb")], null=True
    )
    origin_local_line_items_info_messages = BinaryJSONField(
        constraints=[SQL("DEFAULT '{}'::jsonb")], null=True
    )
    origin_location_ids = ArrayField(
        constraints=[SQL("DEFAULT '{}'::uuid[]")],
        field_class=UUIDField,
        index=True,
        null=True,
    )
    origin_main_port_id = UUIDField(null=True)
    origin_plugin_id = UUIDField(index=True, null=True)
    origin_port_id = UUIDField(null=True)
    origin_trade_id = UUIDField(index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    rate_not_available_entry = BooleanField(
        constraints=[SQL("DEFAULT false")], null=True
    )
    service_provider_id = UUIDField(index=True, null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField()
    validities = BinaryJSONField(null=True)
    weight_limit = BinaryJSONField(null=True)
    weight_limit_id = UUIDField(null=True)

    class Meta:
        table_name = "fcl_freight_rates"


KEYS_TO_KEEP = ["code", "currency", "price", "unit"]

COLUMNS = [
    field for field in FclFreightRateAuditStatistic._meta.fields.keys() if field != "id"
]

SELECT = (
    FclFreightRate.origin_continent_id,
    FclFreightRate.destination_continent_id,
    FclFreightRate.origin_country_id,
    FclFreightRate.destination_country_id,
    FclFreightRate.origin_port_id,
    FclFreightRate.destination_port_id,
    FclFreightRate.cogo_entity_id,
    FclFreightRate.shipping_line_id,
    FclFreightRate.service_provider_id,
    FclFreightRate.commodity,
    FclFreightRate.container_size,
    FclFreightRate.container_type,
    FclFreightRate.importer_exporter_id,
    FclFreightRateAudit.action_name,
    FclFreightRateAudit.performed_by_id,
    FclFreightRateAudit.data,
    FclFreightRateAudit.created_at,
    FclFreightRateAudit.object_id.alias("rate_id"),
)

FIELDS = ",".join(COLUMNS)


def convert_to_date(string):
    try:
        date_format = datetime.fromisoformat(string)
    except:
        try:
            date_format = datetime.strptime(string, "%d-%m-%Y")
        except:
            try:
                date_format = datetime.strptime(string, "%d-%m-%y")
            except:
                pass
    return date_format


def convert_to_datetime(string):
    try:
        return datetime.strptime(string, "%Y-%m-%d %H:%M:%S.%f").strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except:
        return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
            "%Y-%m-%d %H:%M:%S"
        )


def main():
    reset()
    avoid_sources = ["predicted", "rate_extension", "cluster_extension"]
    counter = 1
    t = 0
    rows = []
    audits = []
    query = get_query()
    total_length = query.count()
    for rate in ServerSide(query):
        print(
            f"-------------------------------- INDEX {counter}--------------------------------"
        )

        audit = rate.__dict__["__data__"]
        audit["rate_id"] = rate.__dict__["rate_id"]
        audit.update(rate.__dict__["fclfreightrate"].__dict__["__data__"])

        audit = json_encoder(audit)

        data = audit.get("data", {})

        if (
            not data
            or (data.get("source") in avoid_sources)
            or (data.get("mode") in avoid_sources)
        ):
            continue

        audit["validity_start"] = data.get("validity_start")
        audit["validity_end"] = data.get("validity_end")
        audit["sourced_by_id"] = data.get("sourced_by_id")
        audit["procured_by_id"] = data.get("procured_by_id")

        del audit["data"]

        line_items = data.get("line_items", [])
        if not line_items:
            continue

        for line_item in line_items:
            if "code" in line_item and line_item["code"] != "BAS":
                continue
            audit_row = audit.copy()
            for key in KEYS_TO_KEEP:
                if key not in line_item:
                    del line_item[key]
            line_item["market_price"] = line_item.get("market_price") or 0
            line_item["original_price"] = line_item.get("original_price") or 0
            if line_item["currency"] == Fcl.default_currency.value:
                line_item["standard_price"] = line_item["price"]
            else:
                line_item["standard_price"] = common.get_money_exchange_for_fcl(
                    {
                        "from_currency": line_item["currency"],
                        "to_currency": Fcl.default_currency.value,
                        "price": line_item["price"],
                    }
                ).get("price", line_item["price"])

            audit_row.update(line_item)

            if not audit_row.get("validity_start") or not audit_row.get("validity_end"):
                continue
            if (
                isinstance(audit_row["validity_start"], str)
                and isinstance(audit_row["validity_end"], str)
                and isinstance(audit_row["created_at"], str)
            ):
                audit_row["validity_start"] = audit_row["validity_start"].replace(
                    "/", "-"
                )
                audit_row["validity_end"] = audit_row["validity_end"].replace("/", "-")
                audit_row["created_at"] = audit_row["created_at"].replace("/", "-")
                audit_row["validity_start"] = (
                    convert_to_date(audit_row["validity_start"])
                    .replace(tzinfo=timezone.utc)
                    .strftime("%Y-%m-%d")
                )
                audit_row["validity_end"] = (
                    convert_to_date(audit_row["validity_end"])
                    .replace(tzinfo=timezone.utc)
                    .strftime("%Y-%m-%d")
                )

                audit_row["created_at"] = convert_to_datetime(audit_row["created_at"])

            for key in COLUMNS:
                if key not in COLUMNS:
                    del audit_row[key]

            audit_row = {k: audit_row.get(k) for k in COLUMNS}

            audit_row["id"] = counter

            counter += 1

            audits.append((audit_row))

        rows.extend(audits)

        if len(rows) >= 100000:
            send_to_clickhouse(rows)
            rows = []

        print("Done With", (counter / total_length) * 100)

    if audits:
        send_to_clickhouse(audits)


def send_to_clickhouse(data):
    click = ClickHouse()
    query = f"INSERT INTO brahmastra.{FclFreightRateAuditStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 VALUES"
    columns = FclFreightRateAuditStatistic._meta.fields
    values = []
    for k in data:
        d = {name: k[name] for name in columns}
        value = []
        for k, v in d.items():
            if v is None:
                value.append("DEFAULT")
            elif (
                isinstance(columns[k], UUIDField)
                or isinstance(columns[k], TextField)
                or isinstance(columns[k], CharField)
                or isinstance(columns[k], DateTimeField)
            ):
                value.append(f"'{v}'")
            elif isinstance(columns[k], BooleanField):
                value.append("true" if v else "false")
            else:
                value.append(f"{v}")
        values.append(f"({','.join(value)})")

    if values:
        click.execute(query + ",".join(values))


def reset():
    clicks = Clicks(models=[FclFreightRateAuditStatistic], ignore_oltp=True)

    clicks.delete()

    clicks.create()


def get_query():
    return (
        FclFreightRateAudit.select(*SELECT)
        .where(
            FclFreightRateAudit.object_type == "FclFreightRate",
            FclFreightRateAudit.action_name.in_(["create", "update"]),
        )
        .join(FclFreightRate, on=(FclFreightRateAudit.object_id == FclFreightRate.id))
    )


if __name__ == "__main__":
    main()
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from peewee import SQL
from datetime import datetime, timedelta
import urllib
import json
from playhouse.postgres_ext import ServerSide
from services.bramhastra.helpers.common_statistic_helper import get_identifier
from configs.fcl_freight_rate_constants import (
    DEFAULT_RATE_TYPE,
    DEFAULT_SCHEDULE_TYPES,
    DEFAULT_PAYMENT_TERM,
)
from configs.env import DEFAULT_USER_ID
from micro_services.client import common

STANDARD_CURRENCY = "USD"
PERFORMED_BY_MAPPING_URL = "https://cogoport-production.sgp1.digitaloceanspaces.com/73f7bad75162a7ed48e36d1fd93d015a/performed_mapping.json"
REGION_MAPPING_URL = "https://cogoport-production.sgp1.digitaloceanspaces.com/0860c1638d11c6127ab65ce104606100/id_region_id_mapping.json"
RATE_PARAMS = [
    "commodity",
    "container_size",
    "container_type",
    "destination_country_id",
    "origin_continent_id",
    "destination_continent_id",
    "destination_local_id",
    "destination_detention_id",
    "destination_main_port_id",
    "destination_port_id",
    "destination_trade_id",
    "origin_country_id",
    "origin_local_id",
    "origin_detention_id",
    "origin_demurrage_id",
    "destination_demurrage_id",
    "origin_main_port_id",
    "origin_port_id",
    "origin_trade_id",
    "service_provider_id",
    "shipping_line_id",
    "mode",
    "accuracy",
    "cogo_entity_id",
    "sourced_by_id",
    "procured_by_id",
]


class PopulateRates:

    def get_validity_params(self, validity):
        price = validity.get("price")
        line_items = validity.get("line_items")
        currency = (
            validity.get("currency")
            or validity.get("freight_price_currency")
            or validity.get("freight_price_currency")
            or STANDARD_CURRENCY
        )

        if not price and line_items:
            currency_lists = [
                item["currency"] for item in line_items if item["code"] == "BAS"
            ]
            currency = currency_lists[0]
            if len(set(currency_lists)) != 1:
                price = 0
                for item in line_items:
                    try:
                        price += common.get_money_exchange_for_fcl(
                            {
                                "price": item.get("price") or item.get("buy_price"),
                                "from_currency": item["currency"],
                                "to_currency": currency,
                            }
                        ).get("price", 100)
                    except:
                        price += 100

            else:
                price = float(
                    sum(
                        item.get("price") or item.get("buy_price", 100)
                        for item in line_items
                    )
                )
            pass

        if currency == STANDARD_CURRENCY:
            standard_price = price
        else:
            try:
                standard_price = common.get_money_exchange_for_fcl(
                    {
                        "price": price,
                        "from_currency": currency,
                        "to_currency": STANDARD_CURRENCY,
                    }
                ).get("price", price)
            except:
                standard_price = price

        validity_details = {
            "validity_created_at": validity.get("validity_start"),
            "validity_updated_at": validity.get("validity_start"),
            "price": price,
            "standard_price": standard_price,
            "currency": currency,
            "payment_term": validity.get("payment_term") or DEFAULT_PAYMENT_TERM,
            "schedule_type": validity.get("schedule_type") or DEFAULT_SCHEDULE_TYPES,
            "validity_start": validity.get("validity_start"),
            "validity_end": validity.get("validity_end"),
        }
        return validity_details


    def get_identifier(self, rate_id, validity_id):
        return get_identifier(rate_id,validity_id)
    
    def populate_from_active_rates(self):
        print("\npopulating rates ...")

        query = FclFreightRate.select().where(
            FclFreightRate.id.not_in(
                FclFreightRateStatistic.select(FclFreightRateStatistic.rate_id)
            )
        )

        with urllib.request.urlopen(PERFORMED_BY_MAPPING_URL) as url:
                mappings = json.loads(url.read().decode())
                print('loaded performed by mapping')
                
                PERFORMED_BY_MAPPING = dict()
                
                for mapping in mappings:
                    PERFORMED_BY_MAPPING[mapping.get('object_id')] = mapping
                    
                del mappings
        print("formed query")

        row_data = []

        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())
        count = 0

        print("starting iterator...")
        for rate in ServerSide(query):
            # print(str(rate.id))
            for validity in rate.validities:
                identifier = self.get_identifier(str(rate.id), validity["id"])

                rate_params = {key: getattr(rate, key) for key in RATE_PARAMS}

                validity_params = self.get_validity_params(validity)

                row = {
                    **rate_params,
                    **validity_params,
                    "containers_count": getattr(rate, "containers_count") or 0,
                    "identifier": identifier,
                    "rate_id": getattr(rate, "id"),
                    "rate_created_at": getattr(rate, "created_at"),
                    "rate_updated_at": getattr(rate, "updated_at"),
                    "rate_type": getattr(rate, "rate_type") or DEFAULT_RATE_TYPE,
                    "origin_region_id": REGION_MAPPING.get(
                        getattr(rate, "origin_port_id")
                    ),
                    "destination_region_id": REGION_MAPPING.get(
                        getattr(rate, "destination_port_id")
                    ),
                    "market_price": validity.get("market_price")
                    or validity.get("price"),
                    "validity_id": validity.get("id"),
                }
                
                row["performed_by_id"] = PERFORMED_BY_MAPPING.get(getattr(rate,'id'), {}).get('performed_by_id', DEFAULT_USER_ID)
                row["performed_by_type"] = PERFORMED_BY_MAPPING.get(getattr(rate,'id'), {}).get('performed_by_type','agent')

                row_data.append(row)
                count += 1
                print(count)
                if count == 30000:
                    FclFreightRateStatistic.insert_many(row_data).execute()
                    print("\ninserted 30k\n")
                    count = 0
                    row_data = []
        if row_data:
            FclFreightRateStatistic.insert_many(row_data).execute()

populate_rates = PopulateRates()

# This will populate all the remaining rates which are not present in statistics
# They should have non-empty validities
populate_rates.populate_from_active_rates()