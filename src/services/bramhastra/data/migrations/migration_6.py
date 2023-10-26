from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.postgres_ext import ServerSide
from services.bramhastra.helpers.common_statistic_helper import get_fcl_freight_identifier
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from micro_services.client import common
from services.bramhastra.enums import Fcl
from datetime import datetime
from peewee import SQL


def main():
    fcl_freight_rates = FclFreightRate.select().where(
        (FclFreightRate.validities.is_null(False))
        & (FclFreightRate.validities != SQL("'[]'"))
        & (FclFreightRate.last_rate_available_date >= datetime.now())
    )
    
    count = 0

    for fcl_freight_rate in ServerSide(fcl_freight_rates):
        print("id",fcl_freight_rate.id)
        print(count)
        for validity in fcl_freight_rate.validities:
            fcl_freight_rate_statistic = (
                FclFreightRateStatistic.select()
                .where(
                    FclFreightRateStatistic.identifier
                    == get_fcl_freight_identifier(fcl_freight_rate.id, validity.get("id"))
                )
                .first()
            )
            for line_item in validity.get("line_items", []):
                if fcl_freight_rate_statistic:
                    if line_item.get("code") == "BAS":
                        fcl_freight_rate_statistic.bas_price = line_item.get("price") or 0
                        fcl_freight_rate_statistic.bas_currency = line_item.get("currency")
                        if line_item["currency"] == Fcl.default_currency.value:
                            fcl_freight_rate_statistic.bas_standard_price = line_item.get(
                                "price"
                            ) or 0
                        else:
                            fcl_freight_rate_statistic.bas_standard_price = (
                                common.get_money_exchange_for_fcl(
                                    {
                                        "from_currency": line_item["currency"],
                                        "to_currency": Fcl.default_currency.value,
                                        "price": line_item["price"],
                                    }
                                ).get("price", line_item["price"])
                            )

                    fcl_freight_rate_statistic.save()
                
                count+=1


if __name__ == "__main__":
    main()
