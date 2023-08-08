from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from datetime import datetime,timedelta
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_supply_agents
from micro_services.client import common

def send_expired_air_freight_rate_notification():
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)
    fifteen_days_ago = now - timedelta(days=15)

    rates_expired = (AirFreightRate
                .select(AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id)
                .where(
                    AirFreightRate.rate_not_available_entry == 'false',
                    AirFreightRate.last_rate_available_date <= one_day_ago,
                    AirFreightRate.created_at >= fifteen_days_ago
                )
                .group_by(AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id))
    rates_expired_count = jsonable_encoder(list(rates_expired.dicts()))
    if not rates_expired:
        return 
    rates_expired_count = len(rates_expired_count)
    send_communication(rates_expired_count)

def send_communication(rates_expired_count):
    supply_agents = get_supply_agents()
    for supply_agent in supply_agents:
        data = {
        'type': 'platform_notification',
        'user_id': supply_agent['user_id'],
        'service': 'air_freight_rate',
        'service_id': supply_agent['user_id'],
        'template_name': 'air_international_rates_expired_notification',
        'variables': { 'rates_expired_count': rates_expired_count }
    }
        common.create_communication(data)