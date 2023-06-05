from micro_services.client import common

def format_air_freight_rate(rate, locations):
    print(rate)
    rate_obj = {
        'origin_airport_id': locations['origin']['id'],
        'destination_airport_id': locations['destination']['id']
    }
    return rate_obj
def create_proper_json(rates):
    return rates


def create_air_freight_rate_api(rate, locations):
    rate_obj = format_air_freight_rate(rate=rate, locations=locations)
    common.create_air_freight_rate(rate_obj)


def create_freight_look_rates(rates):
    print(rates, 'NEW RATES')
    proper_json_rates = create_proper_json(rates)

    locations = {
        'origin': {
            'id': ''
        },
        'destination': {
            'id': ''
        }
    }

    # for rate in proper_json_rates:
    #     create_air_freight_rate_api(rate, locations)

    # print(rates)
    return 'HII RMS'