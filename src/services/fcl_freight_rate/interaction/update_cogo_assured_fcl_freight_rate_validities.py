from datetime import datetime, timedelta
import uuid
from fastapi.encoders import jsonable_encoder
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.cogo_assured_rate_constants import FCL_FREIGHT_RATE_DISCOUNT_GREATER_THAN_1000, FCL_FREIGHT_RATE_DISCOUNT_LESS_THAN_EQUAL_TO_1000
from configs.fcl_freight_rate_constants import COGO_ASSURED_SHIPPING_LINE_ID, COGO_ASSURED_SERVICE_PROVIDER_ID, DEFAULT_RATE_TYPE

def get_system_rates(request):
    fcl_rate = FclFreightRate.select(
        FclFreightRate.validities,
        FclFreightRate.id
    ).where(
        FclFreightRate.origin_port_id == request.get('origin_port_id'),
        FclFreightRate.destination_port_id == request.get('destination_port_id'),
        FclFreightRate.origin_main_port_id == request.get('origin_main_port_id'),
        FclFreightRate.destination_main_port_id == request.get('destination_main_port_id'),
        FclFreightRate.service_provider_id != COGO_ASSURED_SERVICE_PROVIDER_ID,
        FclFreightRate.container_size == request.get('container_size'),
        FclFreightRate.container_type == request.get('container_type'),
        FclFreightRate.commodity == request.get('commodity'),
        FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
        ~FclFreightRate.rate_not_available_entry,
        FclFreightRate.last_rate_available_date >= datetime.now().date(),
        FclFreightRate.mode == 'manual'
    )
    return jsonable_encoder(list(fcl_rate.dicts()))

def update_cogo_assured_fcl_freight_rate_validities(rate):
    cogo_assured_rate = rate
    before_modification_prices = {}
    for validity in cogo_assured_rate['validities']:
        validity_start = datetime.fromisoformat(validity["validity_start"]).date()
        validity_end = datetime.fromisoformat(validity["validity_end"]).date()
        current_date = datetime.now().date()
        
        if validity_end >= current_date:
            currency = validity["currency"]
            
            existing_system_rates =  get_system_rates(request=cogo_assured_rate)
            key = cogo_assured_rate["container_size"] + cogo_assured_rate["container_type"] + cogo_assured_rate["commodity"]
            before_modification_prices[key] = validity["price"]
            initial_first_week_price = get_initial_first_week_price(existing_system_rates, validity["price"], cogo_assured_rate, cogo_assured_rate["container_size"], cogo_assured_rate["container_type"], cogo_assured_rate["commodity"], before_modification_prices)
            
            if not initial_first_week_price:
                break
            
            week_1_rate = set_week_rate(initial_first_week_price, initial_first_week_price, 1)
            second_week_price = get_second_week_price(existing_system_rates, validity["price"], week_1_rate)
            week_2_rate = set_week_rate(second_week_price, week_1_rate, 2)
            week_3_rate = set_week_rate(week_2_rate, week_1_rate, 3)
            week_4_rate = set_week_rate(week_3_rate, week_1_rate, 4)
            week_5_rate = set_week_rate(week_4_rate, week_1_rate, 5)
            new_validities = get_new_validities(week_1_rate, week_2_rate, week_3_rate, week_4_rate, week_5_rate, validity_start, validity_end, currency)
            validity_end = new_validities[-1]["validity_end"]
            new_validities = jsonable_encoder(new_validities)
            FclFreightRate.update(validities = new_validities, last_rate_available_date = validity_end, updated_at = datetime.now()).where(FclFreightRate.id == cogo_assured_rate['id']).execute()
            break

def get_initial_first_week_price(existing_system_rates, current_price, cogo_assured_rate, container_size, container_type, commodity, before_modification_prices):
    relevant_rates = []
    if existing_system_rates:
        for rate in existing_system_rates:
          validities = rate['validities']
          for t in validities:
              validity_start = datetime.fromisoformat(t['validity_start']).date()
              validity_end = datetime.fromisoformat(t['validity_end']).date()
              current_date = datetime.now().date()
              if validity_start <=current_date and validity_end >= current_date:
                  relevant_rates.append(t['price'])
                  break
        if len(relevant_rates):
            return min(relevant_rates)

    if container_size in ['40', '40HC']:
        key = "20{}{}".format(container_type, commodity)
        twenty_feet_price = None
        if key in before_modification_prices and before_modification_prices[key]:
            twenty_feet_price = before_modification_prices[key]
        twenty_feet_rate = cogo_assured_rate
        if not twenty_feet_price and twenty_feet_rate:
            for t in twenty_feet_rate['validities']:
                validity_start = datetime.fromisoformat(t['validity_start']).date()
                validity_end = datetime.fromisoformat(t['validity_end']).date()
                current_date = datetime.now().date()
                if validity_start <=current_date and validity_end >= current_date:
                  relevant_rates.append(t['price'])
                  break
        if twenty_feet_price and current_price * 1.01 < twenty_feet_price:
            return twenty_feet_price + [0.5, current_price / twenty_feet_price].max * twenty_feet_price
    current_price * 1.01

def get_second_week_price(existing_system_rates, current_price, week_1_rate):
    if existing_system_rates:
        relevant_rates = []
        for rate in existing_system_rates:
            for t in rate['validities']:
                validity_start = datetime.fromisoformat(t['validity_start']).date()
                validity_end = datetime.fromisoformat(t['validity_end']).date()
                next_week_date = (datetime.now() + timedelta(days=7)).date()
                if validity_start <= next_week_date and validity_end >= next_week_date:
                    relevant_rates.append(t['price'])
        if len(relevant_rates) and min(relevant_rates) < week_1_rate:          
            return min(relevant_rates)

    return week_1_rate

def get_formatted_date(date):
    return date

def set_week_rate(previous_week_rate, week_1_rate, curr_week):
    if previous_week_rate > 1000:
     return week_1_rate - FCL_FREIGHT_RATE_DISCOUNT_GREATER_THAN_1000[curr_week]
    else:
      return previous_week_rate * FCL_FREIGHT_RATE_DISCOUNT_LESS_THAN_EQUAL_TO_1000[curr_week]

def get_new_validities(week_1_rate, week_2_rate, week_3_rate, week_4_rate, week_5_rate, validity_start, validity_end, currency):
    new_validities = []

    new_validities.append({ 'id': str(uuid.uuid4()), 'price': int(week_1_rate or 0), 'currency': currency, 'validity_start': validity_start, 'validity_end': validity_start + timedelta(days=6), 'line_items': [{ 'code': 'BAS', 'unit': 'per_container', 'price': int(week_1_rate or 0), 'currency': currency }] })
    new_validities.append({ 'id': str(uuid.uuid4()), 'price': int(week_2_rate or 0), 'currency': currency, 'validity_start': validity_start + timedelta(days=7),  'validity_end': validity_start + timedelta(days=13), 'line_items': [{ 'code': 'BAS', 'unit': 'per_container', 'price': int(week_2_rate or 0), 'currency': currency }] })
    new_validities.append({ 'id': str(uuid.uuid4()), 'price': int(week_3_rate or 0), 'currency': currency, 'validity_start': validity_start + timedelta(days=14), 'validity_end': validity_start + timedelta(days=20), 'line_items': [{ 'code': 'BAS', 'unit': 'per_container', 'price': int(week_3_rate or 0), 'currency': currency }] })
    new_validities.append({ 'id': str(uuid.uuid4()), 'price': int(week_4_rate or 0), 'currency': currency, 'validity_start': validity_start + timedelta(days=21), 'validity_end': validity_start + timedelta(days=27), 'line_items': [{ 'code': 'BAS', 'unit': 'per_container', 'price': int(week_4_rate or 0), 'currency': currency }] })
    new_validities.append({ 'id': str(uuid.uuid4()), 'price': int(week_5_rate or 0), 'currency': currency, 'validity_start': validity_start + timedelta(days=28), 'validity_end': validity_start + timedelta(days=34), 'line_items': [{ 'code': 'BAS', 'unit': 'per_container', 'price': int(week_5_rate or 0), 'currency': currency }] })

    return new_validities
