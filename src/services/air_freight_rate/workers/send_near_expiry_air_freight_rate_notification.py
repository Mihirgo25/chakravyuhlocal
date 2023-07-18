from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_supply_agents
from micro_services.client import common
from datetime import datetime,timedelta
from peewee import fn
def send_near_expiry_air_freight_rate_notification():
    rates_about_to_expire = (AirFreightRate
                         .select(AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id)
                         .where(
                             AirFreightRate.rate_not_available_entry == 'false',
                             (fn.DATE(AirFreightRate.last_rate_available_date) == datetime.now().date() + timedelta(days=7))
                         )
                         .group_by(AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id)) 
    rates_about_to_expire = jsonable_encoder(list(rates_about_to_expire.dicts()))
    if not rates_about_to_expire:
        return 
    
    rates_about_to_expire_next_day = (AirFreightRate
         .select(AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id)
         .where(AirFreightRate.rate_not_available_entry == False ,
                (fn.DATE(AirFreightRate.last_rate_available_date) ==  datetime.now().date() + timedelta(days=1)))
         .group_by(AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id))
    rates_about_to_expire_next_day = jsonable_encoder (list(rates_about_to_expire_next_day.dicts()))

    if not rates_about_to_expire_next_day:
        return
    
    send_communication(len(rates_about_to_expire),len(rates_about_to_expire_next_day))

def send_communication(rates_expiring_count, rates_about_to_expire_next_day):

    supply_agents = get_supply_agents()

    for supply_agent in supply_agents:
      data = {
        'type': 'platform_notification',
        'user_id': supply_agent['user_id'],
        'service': 'air_freight_rate',
        'service_id': supply_agent['user_id'],
        'template_name': 'air_international_rates_expiring_notification',
        'variables': { 'rates_expiring_count': rates_expiring_count, 'day': '7 days' }
      }
      common.create_communication(data)
      data['variables']['day'] = 'day'
      data['variables']['rates_expiring_count'] = rates_about_to_expire_next_day
      if rates_about_to_expire_next_day > 0:
          common.create_communication(data)