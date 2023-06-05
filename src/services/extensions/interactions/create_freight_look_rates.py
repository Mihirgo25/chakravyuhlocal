from micro_services.client import common

def format_air_freight_rate(rate, locations):
    print(rate)
    rate_obj = {
        'origin_airport_id': locations['origin']['id'],
        'destination_airport_id': locations['destination']['id']
    }
    return rate_obj

def read_json():
    import json
    f = open('/Users/ssngurjar/chakravyuh/src/services/extensions/interactions/r.json')
    data = json.load(f)
    f.close()
    return data

def create_proper_json(rates):
    headers = rates[0]
    new_rates_obj = rates[1: len(rates)]
    final_rates = []
    for rate in new_rates_obj:
        obj = {}
        for i, item in enumerate(rate):
            key = headers[i]
            obj[key] = item
        final_rates.append(obj)

    return final_rates


def create_air_freight_rate_api(rate, locations):
    rate_obj = format_air_freight_rate(rate=rate, locations=locations)
    common.create_air_freight_rate(rate_obj)


def create_freight_look_rates(request):
    rates = request['rates']
    destination = request.get('destination')
    new_rates = read_json()
    proper_json_rates = create_proper_json(new_rates)
    # print(proper_json_rates[0])

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
    return proper_json_rates