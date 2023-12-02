from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from peewee import fn
from datetime import datetime, timedelta
import urllib
import json
from playhouse.postgres_ext import ServerSideQuery
from services.bramhastra.helpers.common_statistic_helper import (
    get_fcl_freight_identifier,
)
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
        return get_fcl_freight_identifier(rate_id, validity_id)

    def populate_from_active_rates(self):
        print("populating rates ...")

        with urllib.request.urlopen(PERFORMED_BY_MAPPING_URL) as url:
            mappings = json.loads(url.read().decode())
            print("loaded performed by mapping...")
            PERFORMED_BY_MAPPING = dict()
            for mapping in mappings:
                PERFORMED_BY_MAPPING[mapping.get("object_id")] = mapping
            del mappings

        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())
            print("loaded REGION_MAPPING...")

        row_data = []

        updated_at_bounds = list(
            FclFreightRate.select(
                fn.MIN(FclFreightRate.updated_at).cast("date").alias("min_updated_at"),
                fn.MAX(FclFreightRate.updated_at).cast("date").alias("max_updated_at"),
                (
                    fn.MAX(FclFreightRate.updated_at).cast("date")
                    - fn.MIN(FclFreightRate.updated_at).cast("date")
                ).alias("days_diff"),
            ).dicts()
        )[0]
        minutes_diff = (updated_at_bounds.get("days_diff") + 1) * 24 * 60
        min_updated_at = str(updated_at_bounds.get("min_updated_at"))
        print("\nMin Updated at:", min_updated_at)
        print("Max Updated at:", updated_at_bounds.get("max_updated_at"))
        print("Minutes Diff:", minutes_diff, "\n")

        minute_cntr = 0
        MINUTES_RANGE = 21600

        while minute_cntr <= minutes_diff:
            subquery = FclFreightRateStatistic.select(
                fn.DISTINCT(FclFreightRateStatistic.rate_id)
            )
            query = FclFreightRate.select().where(
                FclFreightRate.updated_at
                >= (
                    datetime.strptime(min_updated_at, "%Y-%m-%d")
                    + timedelta(minutes=minute_cntr)
                ),
                FclFreightRate.updated_at
                <= (
                    datetime.strptime(min_updated_at, "%Y-%m-%d")
                    + timedelta(minutes=minute_cntr + MINUTES_RANGE)
                ),
                (~FclFreightRate.id << subquery),
            )

            print(f"\n:: minute = {minute_cntr} / {minutes_diff} ::", end=" ")
            for rate in ServerSideQuery(query):
                try:
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
                            "rate_type": getattr(rate, "rate_type")
                            or DEFAULT_RATE_TYPE,
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

                        row["performed_by_id"] = PERFORMED_BY_MAPPING.get(
                            getattr(rate, "id"), {}
                        ).get("performed_by_id", DEFAULT_USER_ID)
                        row["performed_by_type"] = PERFORMED_BY_MAPPING.get(
                            getattr(rate, "id"), {}
                        ).get("performed_by_type", "agent")

                        row_data.append(row)
                except Exception as e:
                    print(e)
                    breakpoint()

            if len(row_data) >= 10000:
                FclFreightRateStatistic.insert_many(row_data).execute()
                print(f"\n-- inserted {round(len(row_data)/1000,1)}K --")
                row_data = []

            minute_cntr += MINUTES_RANGE
            print(len(row_data), end="")

        if row_data:
            FclFreightRateStatistic.insert_many(row_data).execute()


if __name__ == "__main__":
    #30144
    PopulateRates().populate_from_active_rates()
