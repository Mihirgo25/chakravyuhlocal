from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import get_road_distance

def get_ftl_freight_rate_extension(query, request):
    ftl_rates_extended = list(query.dicts())
    new_list = []

    if ftl_rates_extended:
        requested_distance = get_road_distance(request.get('origin_location_id'), request.get('destination_location_id'))
        price_by_code = {}
        code_count = {}
        unit_val = ''

        for item in ftl_rates_extended:
            distance = get_road_distance(str(item.get('origin_location_id')), str(item.get('destination_location_id')))
            for line_item in item.get("line_items", []):
                code = line_item.get("code")
                price_per_km = line_item.get("price") / distance
                unit_val = line_item.get('unit')

                if code not in price_by_code:
                    price_by_code[code] = 0
                    code_count[code] = 0
                
                price_by_code[code] += price_per_km
                code_count[code] += 1

        average_prices = {code: price_by_code[code] / code_count[code] for code in code_count}
        new_list = [ftl_rates_extended[0].copy()]
        new_list[0]["line_items"] = [
            {
                "code": code,
                "price": avg_per_km * requested_distance,
                "unit": unit_val,
                "currency": "INR", ## POSSIBLE BREAKAGE, WHAT IF OTHER CURRENCIES ARE PRESENT
                "remarks": []
            }
            for code, avg_per_km in average_prices.items()
        ]

    return new_list