from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.chakravyuh.setters.fcl_freight import FclFreightVyuh as FclFreightVyuhSetter
from fastapi.encoders import jsonable_encoder
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from datetime import datetime



def create_fcl_transformation():

    current_date =  datetime.now().date()
    rates = FclFreightRate.select(
        FclFreightRate.id,
        FclFreightRate.origin_location_ids,
        FclFreightRate.destination_location_ids,
        FclFreightRate.container_size,
        FclFreightRate.container_type,
        FclFreightRate.commodity,
        FclFreightRate.shipping_line_id,
        FclFreightRate.origin_port_id,
        FclFreightRate.destination_port_id,
        FclFreightRate.origin_country_id,
        FclFreightRate.destination_country_id,
        FclFreightRate.origin_trade_id,
        FclFreightRate.destination_trade_id,
        FclFreightRate.validities,
        FclFreightRate.mode,
        FclFreightRate.service_provider_id,
    ).where(
        FclFreightRate.last_rate_available_date > current_date,
        FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
        ~FclFreightRate.rate_not_available_entry
    ).order_by(FclFreightRate.id.desc())

    total_rates = rates.count()

    print(total_rates)

    c = 0

    OFFSET = 0
    BATCH_SIZE = 5000

    created_transformations = {}

    while OFFSET <= total_rates:
        limited_rates_query = rates.offset(OFFSET).limit(5000)
        OFFSET = OFFSET + BATCH_SIZE

        limited_rates = jsonable_encoder(list(limited_rates_query.dicts()))

        for rate in limited_rates:
            current_validities = rate['validities'] or []
            new_validity = current_validities[0]
            new_rate = rate | {
                'schedule_type': new_validity['schedule_type'],
                'payment_term': new_validity['payment_term'],
                'line_items': current_validities[0]['line_items']
            }
            keyP = '{}:{}:{}:{}'.format(new_rate['origin_port_id'], new_rate['destination_port_id'], new_rate['container_size'], new_rate['container_type'])
            keyC = '{}:{}:{}:{}'.format(new_rate['origin_country_id'], new_rate['destination_country_id'], new_rate['container_size'], new_rate['container_type'])
            keyT = '{}:{}:{}:{}'.format(new_rate['origin_trade_id'], new_rate['destination_trade_id'], new_rate['container_size'], new_rate['container_type'])
            what_to_create = {
                'seaport': True,
                'country': True,
                'trade': True
            }
            if keyP in created_transformations:
                what_to_create['seaport'] = False
            if keyC in created_transformations:
                what_to_create['country'] = False
            if keyT in created_transformations:
                what_to_create['trade'] = False

            fcl_freight_vyuh = FclFreightVyuhSetter(new_rate=new_rate, current_validities=current_validities, what_to_create=what_to_create)
            fcl_freight_vyuh.set_dynamic_pricing()
            c = c+1
            created_transformations[keyP] = True
            created_transformations[keyC] = True
            created_transformations[keyT] = True
            print(c, 'Done')