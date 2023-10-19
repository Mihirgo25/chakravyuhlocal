from services.ftl_freight_rate.interactions.create_ftl_freight_rate import create_ftl_freight_rate
from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import get_road_distance
from configs.ftl_freight_rate_constants import ENVISION_USER_ID, PREDICTED_PRICE_SERVICE_PROVIDER
from datetime import datetime,timedelta
from micro_services.client import common
import statistics

def get_ftl_freight_rate_extension(ftl_rates_extended, request):
    new_list = []

    if ftl_rates_extended:
        # distance of requested route
        requested_distance = get_road_distance(request.get('origin_location_id'), request.get('destination_location_id'))
        min_chargeable_weights_list = []
        count_by_code = {}

        final_line_items = [{"code": "BAS", "unit": "per_truck", "price": 0, "remarks": [], "currency": "INR"}, {"code": "FSC", "unit": "per_truck", "price": 0, "remarks": [], "currency": "INR"}]
        for ftl_rate in ftl_rates_extended:
            truck_body_type = ftl_rate.get('truck_body_type')
            unit = ftl_rate.get('unit')
            min_chargeable_weights_list.append(ftl_rate.get('minimum_chargeable_weight'))
            # distance of existing route
            distance = get_road_distance(str(ftl_rate.get('origin_location_id')), str(ftl_rate.get('destination_location_id')))
            # calculate mean price
            final_line_items = get_calculated_line_items(final_line_items, ftl_rate.get("line_items", []), distance, requested_distance, count_by_code)
        # divide by count for mean price
        for final_item in final_line_items:
            final_item['price'] = final_item['price'] / count_by_code[final_item['code']]

        detention_free_time = 1
        transit_time = round((requested_distance//250)*24)
        if transit_time == 0:
            transit_time = 24

        validity_start = datetime.now().date()
        validity_end = (datetime.now() + timedelta(days = 2)).date()
        # calculate median value for minimum_chargeable_weights
        min_chargeable_weights_list = [item for item in min_chargeable_weights_list if item is not None]
        median_minimum_chargeable_weight = None
        if min_chargeable_weights_list:
            median_minimum_chargeable_weight = statistics.median(min_chargeable_weights_list)
        

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
            'line_items': final_line_items,
            'truck_body_type': truck_body_type,
            'transit_time': transit_time,
            'detention_free_time': detention_free_time,
            'validity_start': validity_start,
            'validity_end': validity_end,
            'minimum_chargeable_weight': median_minimum_chargeable_weight,
            'unit': unit,
            'source': 'rate_extension'
        }

        # create extended freight rate
        extended_rate = create_ftl_freight_rate(params)
        params['id'] = str(extended_rate['id'])
        new_list.append(params)
    
    return new_list


def get_calculated_line_items(final_line_items, new_line_items, distance, requested_distance, count_by_code):
    for line_item in new_line_items:
        total_price = line_item.get("price",0)
        code = line_item["code"]
        # calculate count for each FTL Charge
        if code not in count_by_code:
            count_by_code[code] = 0
        count_by_code[code] += 1
        # convert percentage_of_freight to per_truck (FSC)
        if line_item["code"] == "FSC" and line_item["unit"] == "percentage_of_freight":
            required_line_items = new_line_items
            for required_line_item in required_line_items:
                if required_line_item["code"] != "BAS":
                    continue
                total_price = float(required_line_item.get("price",0))
                total_price = (total_price * float(line_item.get("price",0))/100)
        # convert currencies to INR
        if line_item["currency"] != 'INR':
            total_price = convert_to_inr(total_price, line_item["currency"])
        # summation of prices by code
        for final_item in final_line_items:
            if final_item['code'] == line_item['code']:
                final_price = final_item.get("price")
                final_price = ((final_price/requested_distance) + (total_price/distance)) * requested_distance
                final_item['price'] = final_price
    
    return final_line_items

def convert_to_inr(price, currency):
    price = common.get_money_exchange_for_fcl(
        {
            "price": price,
            "from_currency": currency,
            "to_currency": "INR"
        }
    )["price"]
    return price