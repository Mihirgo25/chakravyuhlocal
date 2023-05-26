from services.air_freight_rate.models.air_freight_rate_local import AirFreightRate
def list_air_freight_rate_locals():
    query=get_query()
def get_query():
    query=AirFreightRate.select(
            AirFreightRate.id,
            AirFreightRate.airport_id,
            AirFreightRate.country_id,
            AirFreightRate.trade_id,
            AirFreightRate.continent_id,

        ).order_by()
    return query
