from services.bramhastra.helpers.common_statistic_helper import get_identifier
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)


class Checkout:
    def __init__(self, params) -> None:
        self.common_params = None
        self.checkout_params = []
        self.increment_keys = {"checkout_count"}
        self.params = params

    def set_format_and_existing_rate_stats(self):
        self.common_params = self.params.dict(exclude={"checkout_fcl_freight_services"})
        for param in self.params.checkout_fcl_freight_services:
            rate = param.rate.dict(include={"rate_id", "validity_id"})
            total_buy_price = 0
            for line_item in param.rate.line_items:
                total_buy_price += line_item["total_buy_price"]
            checkout_param = self.common_params.copy()
            checkout_param.update(param.dict(exclude={"rate"}))
            checkout_param["total_buy_price"] = total_buy_price
            checkout_param["currency"] = param.rate.line_items[0]["currency"]
            checkout_param.update(rate)

            fcl_freight_rate_statistic = (
                FclFreightRateStatistic.select()
                .where(FclFreightRateStatistic.identifier == get_identifier(**rate))
                .first()
            )

            if fcl_freight_rate_statistic:
                for k in self.increment_keys:
                    setattr(
                        fcl_freight_rate_statistic,
                        k,
                        getattr(fcl_freight_rate_statistic, k) + 1,
                    )
                
                fcl_freight_rate_statistic.updated_at = self.params.updated_at
                
                fcl_freight_rate_statistic.save()
                
                checkout_param[
                    "fcl_freight_rate_statistic_id"
                ] = fcl_freight_rate_statistic.id
                self.checkout_params.append(checkout_param)
                
    def update_rate(self):
        pass

    def create(self) -> int:
        return CheckoutFclFreightRateStatistic.insert_many(
            self.checkout_params
        ).execute()

    def update(self) -> None:
        pass
