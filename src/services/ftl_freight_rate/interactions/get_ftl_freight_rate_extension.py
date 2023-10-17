from services.ftl_freight_rate.interactions.create_ftl_freight_rate import create_ftl_freight_rate
from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import get_road_distance
from configs.ftl_freight_rate_constants import ENVISION_USER_ID, PREDICTED_PRICE_SERVICE_PROVIDER
from datetime import datetime,timedelta

def get_ftl_freight_rate_extension(ftl_rates_extended, request):
    new_list = []

    if ftl_rates_extended:
        requested_distance = get_road_distance(request.get('origin_location_id'), request.get('destination_location_id'))
        price_by_code_dict = {}
        code_count = {}
        min_chargeable_weights_list = []

        for item in ftl_rates_extended:
            truck_body_type = item.get('truck_body_type')
            unit = item.get('unit')
            min_chargeable_weights_list.append(item.get('minimum_chargeable_weight'))

            distance = get_road_distance(str(item.get('origin_location_id')), str(item.get('destination_location_id')))
            for line_item in item.get("line_items", []):
                code = line_item.get("code")
                price_per_km = line_item.get("price") / distance
                line_item_unit = line_item.get("unit")

                if code not in price_by_code_dict:
                    price_by_code_dict[code] = {
                        "price_per_km": [],
                        "unit": line_item_unit,
                        "currency": "INR"
                    }
                    code_count[code] = 0
                
                price_by_code_dict[code]['price_per_km'].append(price_per_km)
                code_count[code] += 1

            avereage_price_per_km = {code: sum(price_by_code_dict[code]['price_per_km']) / code_count[code] for code in code_count}
            line_items_extension = [
                {
                    "code": code,
                    "price": avg_per_km * requested_distance,
                    "unit": price_by_code_dict[code]['unit'],
                    "currency": price_by_code_dict[code]['currency'],
                    "remarks": []
                }
                for code, avg_per_km in avereage_price_per_km.items()
            ]

        detention_free_time = 1
        transit_time = round((requested_distance//250)*24)
        if transit_time == 0:
            transit_time = 24

        validity_start = datetime.now().date()
        validity_end = (datetime.now() + timedelta(days = 2)).date()
        median_minimum_chargeable_weight = find_median(min_chargeable_weights_list)

        params = {
            'origin_location_id': request.get('origin_location_id'),
            'destination_location_id': request.get('destination_location_id'),
            'trip_type': request.get('trip_type'),
            'truck_type': request.get('truck_type'),
            'commodity': request.get('commodity'),
            'service_provider_id': PREDICTED_PRICE_SERVICE_PROVIDER,
            'performed_by_id': ENVISION_USER_ID,
            'procured_by_id': ENVISION_USER_ID,
            'sourced_by_id': ENVISION_USER_ID,
            'line_items': line_items_extension,
            'truck_body_type': truck_body_type,
            'transit_time': transit_time,
            'detention_free_time': detention_free_time,
            'validity_start': validity_start,
            'validity_end': validity_end,
            'minimum_chargeable_weight': median_minimum_chargeable_weight,
            'unit': unit,
            'source': 'rate_extension'
        }

        create_ftl_freight_rate(params)

        new_list.append(params)

    return new_list

def find_median(unordered_list):
    sorted_list = sorted(unordered_list)
    list_length = len(sorted_list)

    if list_length % 2 == 1:
        median = sorted_list[list_length // 2]
    else:
        mid1 = sorted_list[(list_length - 1) // 2]
        mid2 = sorted_list[list_length // 2]
        median = (mid1 + mid2) / 2

    return median