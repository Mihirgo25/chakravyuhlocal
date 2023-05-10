from services.chakravyuh.models.fcl_freight_rate_local_estimation import FclFreightRateLocalEstimation
from peewee import fn
from micro_services.client import maps

class FclFreightLocalVyuh():
    def __init__(self, rates: list = []):
        self.rates = rates
    
    def check_fulfilment_ratio(self):
        return 100

    def apply_dynamic_price(self):
        print(self.rates)

    def get_eligible_local_estimated_rate(self,request):
        estimated_rate_query = FclFreightRateLocalEstimation.select(
            FclFreightRateLocalEstimation.line_items
        ).where(
            FclFreightRateLocalEstimation.trade_type == request.get('trade_type'),
            FclFreightRateLocalEstimation.container_size == request.get("container_size"),
            FclFreightRateLocalEstimation.container_type == request.get("container_type"),
            FclFreightRateLocalEstimation.commodity == request.get('commodity')
        )
        estimated_rate = self.get_most_eligible_local_estimated_rate(estimated_rate_query, request)
        return estimated_rate

    def get_most_eligible_local_estimated_rate(self, query, request):
        locations_description = maps.list_locations({'filters': {'id': request['port_id']}})

        if locations_description and isinstance(locations_description, dict):
            locations_description = locations_description['list']
        else:
            locations_description = []

        if len(locations_description) > 0:
            trade_id =  locations_description[0].get('trade_id')
            continent_id = locations_description[0].get('continent_id')
        else:
            trade_id = None
            continent_id = None

        country_wise_query = query.where(
            FclFreightRateLocalEstimation.location_id == request['country_id']
        )
        trade_wise_query = query.where(
            FclFreightRateLocalEstimation.location_id == trade_id
        )

        continent_wise_query = query.where(
            FclFreightRateLocalEstimation.location_id == continent_id
        )
        count_query = (
            query.select(
                fn.count(FclFreightRateLocalEstimation.id)
                .filter(
                    (
                        FclFreightRateLocalEstimation.location_id == request['country_id']
                    )
                )
                .over()
                .alias("country_wise"),
                fn.count(FclFreightRateLocalEstimation.id)
                .filter(
                    (
                        FclFreightRateLocalEstimation.location_id == trade_id
                    )
                )
                .over()
                .alias("trade_wise"),
                fn.count(FclFreightRateLocalEstimation.id)
                .filter(
                    (
                        FclFreightRateLocalEstimation.location_id == continent_id
                    )
                )
                .over()
                .alias("continent_wise")
            )
        ).limit(1)
        try:
            result = count_query.dicts().get()
        except:
            return {}

        if result["country_wise"] > 0:
            return country_wise_query.dicts().get()

        if result["trade_wise"] > 0:
            return trade_wise_query.dicts().get()
        
        if result["continent_wise"] > 0:
            return continent_wise_query.dicts().get()

        return {}