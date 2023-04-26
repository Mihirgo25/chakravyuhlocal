from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from peewee import fn

class FclFreightVyuh():
    def __init__(self, rates: list = []):
        self.rates = rates
    
    def check_fulfilment_ratio(self):
        return 100

    def apply_dynamic_pricing(self):
        print(self.rates)
        return self.rates

    def get_eligible_estimated_rate(self,request):
        origin_location_ids = [
            request.get("origin_port_id"),
            request.get("origin_country_id"),
            request.get("origin_trade_id"),
        ]
        destination_location_ids = [
            request.get("destination_port_id"),
            request.get("destination_country_id"),
            request.get("destination_trade_id"),
        ]

        estimated_rate = FclFreightRateEstimation.select(
            FclFreightRateEstimation.line_items
        ).where(
            # FclFreightRateEstimation.origin_location_id << origin_location_ids,
            # FclFreightRateEstimation.destination_location_id << destination_location_ids,
            FclFreightRateEstimation.container_size == request["container_size"],
            FclFreightRateEstimation.container_type == request["container_type"],
        )

        estimated_rate = self.get_most_eligible(estimated_rate, request)
        return estimated_rate

    def get_most_eligible(self,query, request):
        port_port = query.where(
            FclFreightRateEstimation.origin_location_id == request.get("origin_port_id"),
            FclFreightRateEstimation.destination_location_id
            == request.get("destination_port_id"),
        )
        country_country = query.where(
            FclFreightRateEstimation.origin_location_id == request.get("origin_country_id"),
            FclFreightRateEstimation.destination_location_id
            == request.get("destination_country_id"),
        )
        port_country = query.where(
            (
                (
                    FclFreightRateEstimation.origin_location_id
                    == request.get("origin_port_id")
                )
                & (
                    FclFreightRateEstimation.destination_location_id
                    == request.get("destination_country_id")
                )
            )
            | (
                (
                    FclFreightRateEstimation.origin_location_id
                    == request.get("origin_country_id")
                )
                & (
                    FclFreightRateEstimation.destination_location_id
                    == request.get("destination_port_id")
                )
            )
        )

        trade_trade = query.where(
            FclFreightRateEstimation.origin_location_id == request.get("origin_trade_id"),
            FclFreightRateEstimation.destination_location_id
            == request.get("destination_trade_id")
        )

        port_trade = query.where(
            ((FclFreightRateEstimation.origin_location_id== request.get("origin_port_id")) & (FclFreightRateEstimation.destination_location_id== request.get("destination_trade_id")))| (
                (FclFreightRateEstimation.origin_location_id == request.get("origin_trade_id"))& (FclFreightRateEstimation.destination_location_id == request.get("destination_port_id"))))

        country_trade = query.where(
            ((FclFreightRateEstimation.origin_location_id== request.get("origin_country_id")) & (FclFreightRateEstimation.destination_location_id== request.get("destination_trade_id")))| (
                (FclFreightRateEstimation.origin_location_id == request.get("origin_trade_id"))& (FclFreightRateEstimation.destination_location_id == request.get("destination_country_id"))))

        count_query = (
            query.select(
                fn.count(FclFreightRateEstimation.id)
                .filter(
                    (
                        FclFreightRateEstimation.origin_location_id
                        == request.get("origin_port_id")
                    )
                    & (
                        FclFreightRateEstimation.destination_location_id
                        == request.get("destination_port_id")
                    )
                )
                .over()
                .alias("port_port"),
                fn.count(FclFreightRateEstimation.id)
                .filter(
                    (
                        FclFreightRateEstimation.origin_location_id
                        == request.get("origin_country_id")
                    )
                    & (
                        FclFreightRateEstimation.destination_location_id
                        == request.get("destination_country_id")
                    )
                )
                .over()
                .alias("country_country"),
                fn.count(FclFreightRateEstimation.id)
                .filter(
                    (
                        (
                            FclFreightRateEstimation.origin_location_id
                            == request.get("origin_port_id")
                        )
                        & (
                            FclFreightRateEstimation.destination_location_id
                            == request.get("destination_country_id")
                        )
                    )
                    | (
                        (
                            FclFreightRateEstimation.origin_location_id
                            == request.get("origin_country_id")
                        )
                        & (
                            FclFreightRateEstimation.destination_location_id
                            == request.get("destination_port_id")
                        )
                    )
                )
                .over()
                .alias("port_country"),
                fn.count(FclFreightRateEstimation.id).filter((FclFreightRateEstimation.origin_location_id == request.get("origin_trade_id")) &
            (FclFreightRateEstimation.destination_location_id== request.get("destination_trade_id"))).over().alias("trade_trade"),
                fn.count(FclFreightRateEstimation.id).filter(   (
                        (
                            FclFreightRateEstimation.origin_location_id
                            == request.get("origin_trade_id")
                        )
                        & (
                            FclFreightRateEstimation.destination_location_id
                            == request.get("destination_country_id")
                        )
                    )
                    | (
                        (
                            FclFreightRateEstimation.origin_location_id
                            == request.get("origin_country_id")
                        )
                        & (
                            FclFreightRateEstimation.destination_location_id
                            == request.get("destination_trade_id")
                        )
                    )).over().alias("country_trade"),
                fn.count(FclFreightRateEstimation.id).filter(   (
                        (
                            FclFreightRateEstimation.origin_location_id
                            == request.get("origin_port_id")
                        )
                        & (
                            FclFreightRateEstimation.destination_location_id
                            == request.get("destination_trade_id")
                        )
                    )
                    | (
                        (
                            FclFreightRateEstimation.origin_location_id
                            == request.get("origin_trade_id")
                        )
                        & (
                            FclFreightRateEstimation.destination_location_id
                            == request.get("destination_port_id")
                        )
                    )).over().alias("port_trade")
            )
        ).limit(1)
        try:
            result = count_query.dicts().get()
        except:
            return {}

        if result["port_port"] == 1:
            return port_port.dicts().get()
        elif result["port_port"] > 1:
            port_port_result = self.add_shipping_line_commodity(port_port, request)
            if port_port_result:
                return port_port_result
            else:
                return port_port.dicts().get()

        if result["port_country"] == 1:
            try:
                return port_country.dicts().get()
            except Exception as e:
                print(e)
        elif result["port_country"] > 1:
            port_country_result = self.add_shipping_line_commodity(port_country, request)
            if port_country_result:
                return port_country_result
            else:
                return port_country.dicts().get()

        if result["country_country"] == 1:
            return country_country.dicts().get()
        elif result["country_country"] > 1:
            country_country_result = self.add_shipping_line_commodity(port_country, request)
            if country_country_result:
                return country_country_result
            else:
                return country_country.dicts().get()
        
        if result['port_trade']==1:
            return country_country.dicts().get()
        elif result['port_trade']>1:
            port_trade_result = self.add_shipping_line_commodity(port_trade,request)
            if port_trade_result:
                return port_trade_result
            else:
                return port_trade.dicts().get()
        
        if result['country_trade']==1:
            return country_trade.dicts().get()
        elif result['country_trade']>1:
            country_trade_result = self.add_shipping_line_commodity(country_trade,request)
            if country_trade_result:
                return country_trade_result
            else:
                return country_trade_result.dicts().get()
        

        if result['trade_trade']==1:
            return trade_trade.dicts().get()
        elif result['trade_trade']>1:
            trade_trade_result = self.add_shipping_line_commodity(trade_trade,request)
            if trade_trade_result:
                return trade_trade_result
            else:
                return trade_trade_result.dicts().get()

        return {}


    def add_shipping_line_commodity(self,query, request):
        shipping_line = query.where(
            FclFreightRateEstimation.shipping_line_id == request.get("shipping_line_id")
        )
        shipping_line_commodity = shipping_line.where(
            FclFreightRateEstimation.commodity == request.get("commodity")
        )

        count_query = (
            query.select(
                fn.count(FclFreightRateEstimation.id)
                .filter(
                    FclFreightRateEstimation.shipping_line_id
                    == request.get("shipping_line_id")
                )
                .over()
                .alias("shipping_line"),
                fn.count(FclFreightRateEstimation.id)
                .filter(
                    (
                        FclFreightRateEstimation.shipping_line_id
                        == request.get("shipping_line_id")
                    )
                    & (
                        FclFreightRateEstimation.shipping_line_id
                        == request.get("commodity")
                    )
                )
                .over()
                .alias("commodity"),
            )
        ).limit(1)
        result = count_query.dicts().get()

        if result["shipping_line"] == 1:
            return shipping_line.dicts().get()

        if result["shipping_line"] > 1 and result["commodity"] >= 1:
            return shipping_line_commodity.dicts().get()

        if result["shipping_line"] > 1 and result["commodity"] == 0:
            return shipping_line.dicts().get()
        return {}