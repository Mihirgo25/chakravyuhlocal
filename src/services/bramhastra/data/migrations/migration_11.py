from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.postgres_ext import ServerSideQuery
from services.bramhastra.enums import Fcl
from micro_services.client import common
from peewee import fn


def save_object_with_bas_info(obj, line_item):
    try:
        bas_currency = line_item["currency"]
        bas_price = line_item["price"]
        bas_standard_price = line_item["price"]
        if bas_currency != Fcl.default_currency.value:
            bas_standard_price = common.get_money_exchange_for_fcl(
                {
                    "from_currency": bas_currency,
                    "to_currency": Fcl.default_currency.value,
                    "price": bas_price,
                }
            ).get("price", bas_price)

        setattr(obj, "bas_price", bas_price)
        setattr(obj, "bas_standard_price", bas_standard_price)

        obj.save()
        return True
    except Exception as e:
        print("Error: ", e)
        return False


def find_and_fix_zero_BAS_prices():
    total_count = list(
        FclFreightRateStatistic.select(fn.COUNT(FclFreightRateStatistic.id))
        .where(
            (FclFreightRateStatistic.bas_price == 0)
            | (FclFreightRateStatistic.bas_standard_price == 0)
            | (FclFreightRateStatistic.bas_price.is_null(True))
            | (FclFreightRateStatistic.bas_standard_price.is_null(True))
        )
        .dicts()
    ).pop()

    query = FclFreightRateStatistic.select().where(
        (FclFreightRateStatistic.bas_price == 0)
        | (FclFreightRateStatistic.bas_standard_price == 0)
        | (FclFreightRateStatistic.bas_price.is_null(True))
        | (FclFreightRateStatistic.bas_standard_price.is_null(True))
    )
    counter = 0

    for rate in ServerSideQuery(query):
        counter += 1
        print("counter: ", counter, "/", total_count)

        is_updated = False
        validities = list(
            FclFreightRate.select(FclFreightRate.validities)
            .where(FclFreightRate.id == rate.rate_id)
            .dicts()
        )

        if validities != None and len(validities) > 0:
            validities = validities[0].get("validities", [])
            for validity in validities:
                if str(validity.get("id")) == str(rate.validity_id):
                    for line_item in validity.get("line_items"):
                        if line_item.get("code") == "BAS":
                            is_updated = save_object_with_bas_info(rate, line_item)
                if is_updated:
                    break

        if not is_updated:
            audits = list(
                FclFreightRateAudit.select(FclFreightRateAudit.data.alias("audit_data"))
                .where(
                    FclFreightRateAudit.object_id == rate.rate_id,
                    (
                        (FclFreightRateAudit.action_name == "create")
                        | (FclFreightRateAudit.action_name == "update")
                    ),
                )
                .limit(10)
                .dicts()
            )

            for audit in audits:
                line_items = audit["audit_data"].get("line_items", [])
                for line_item in line_items:
                    if line_item.get("code") == "BAS":
                        try:
                            is_updated = save_object_with_bas_info(rate, line_item)
                        except Exception as e:
                            print("Line item error:\n", e)
                    if is_updated:
                        break


if __name__ == "__main__":
    find_and_fix_zero_BAS_prices()
