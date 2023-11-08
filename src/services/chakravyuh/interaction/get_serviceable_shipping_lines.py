from micro_services.client import schedule_client
from configs.fcl_freight_rate_constants import TOP_SHIPPING_LINES_FOR_PREDICTION
from libs.flatten_unique_list import flatten_unique_list

def get_serviceable_shipping_lines(request):
    try:
        data = {
            "origin_port_id": request["origin_port_id"],
            "destination_port_id": request["destination_port_id"],
        }
        resp = schedule_client.get_sailing_schedule_port_pair_serviceability(data)
        for sl_hash in resp:
            sl = sl_hash.get("shipping_lines", [])
            sl = flatten_unique_list(sl)
            sl_hash["shipping_lines"] = sl
        
        serviceable_shipping_lines = update_shipping_lines_hash(resp)
        return serviceable_shipping_lines 
    except:
        return []


def get_top_shipping_lines_for_prediction(shipping_lines):
    filtered_shipping_lines = [
        line for line in shipping_lines if line in TOP_SHIPPING_LINES_FOR_PREDICTION
    ][:10]

    if len(filtered_shipping_lines) < 10 and len(shipping_lines) >= 10:
        non_top_lines = [
            line
            for line in shipping_lines
            if line not in TOP_SHIPPING_LINES_FOR_PREDICTION
        ]
        filtered_shipping_lines.extend(
            non_top_lines[: 10 - len(filtered_shipping_lines)]
        )

    return filtered_shipping_lines


def update_shipping_lines_hash(serviceable_shipping_lines):
    used_shipping_lines = set()
    all_shipping_lines = []
    for sl_hash in serviceable_shipping_lines:
        all_shipping_lines.extend(sl_hash.get("shipping_lines", []))

    top_shipping_lines = get_top_shipping_lines_for_prediction(all_shipping_lines)

    for sl_hash in serviceable_shipping_lines:
        shipping_lines = []
        for line in sl_hash.get("shipping_lines", []):
            if not line in used_shipping_lines and line in top_shipping_lines:
                shipping_lines.append(line)
                used_shipping_lines.add(line)
        sl_hash["shipping_lines"] = shipping_lines

    return serviceable_shipping_lines
