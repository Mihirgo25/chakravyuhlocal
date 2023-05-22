from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import (
    HaulageFreightRateRuleSet,
)
from fastapi import HTTPException
from playhouse.shortcuts import model_to_dict
from playhouse.postgres_ext import SQL
from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import (
    get_transit_time,
)
from configs.haulage_freight_rate_constants import (
    CONTAINER_SIZE_FACTORS,
    DESTINATION_TERMINAL_CHARGES_INDIA,
)


class EuropeHaulageFreightRateEstimator:
    def __init__(self, *_, **__):
        pass

    def estimate(self):
        """
        Primary Function to estimate europe prices
        """
        instance = EuropeHaulageFreightRateEstimator()
        final_price = instance.get_europe_rates(
            commodity=self.commodity,
            load_type=self.load_type,
            containers_count=self.containers_count,
            distance=self.distance,
        )
        return final_price

    def get_europe_rates(self, commodity, load_type, containers_count, distance):
        final_data = {}
        final_data["distance"] = distance
        final_data["currency"] = "EUR"
        final_data["country_code"] = "EU"

        wagon_upper_limit = (
            HaulageFreightRateRuleSet.select()
            .where(
                HaulageFreightRateRuleSet.commodity_class_type == commodity,
                HaulageFreightRateRuleSet.distance >= distance,
                HaulageFreightRateRuleSet.train_load_type == load_type,
                HaulageFreightRateRuleSet.currency == "EUR",
                HaulageFreightRateRuleSet.country_code == "EU",
            )
            .order_by(HaulageFreightRateRuleSet.distance)
        )
        wagon_price_upper_limit = [model_to_dict(item) for item in wagon_upper_limit]

        if not wagon_price_upper_limit:
            raise HTTPException(status_code=400, detail="rates not present")

        price = wagon_price_upper_limit[0]["base_price"]
        price = price * containers_count
        final_data["base_price"] = self.apply_surcharges_for_europe(float(price))

        return final_data

    def apply_surcharges_for_europe(self, price):
        surcharge = 0.15 * price
        development_charges = 0.05 * price
        final_price = price + surcharge + development_charges

        return final_price
