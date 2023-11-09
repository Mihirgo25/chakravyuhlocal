from micro_services.client import schedule_client

def create_sailing_schedules_port_pair_coverages(request):
    origin_location = request["origin_location"]
    destination_location = request["destination_location"]
    
    if not request.get('shipping_line_id') or not all(location.get('type') == 'seaport' for location in [origin_location, destination_location]):
        return False

    origin_port_type = "icd_port" if origin_location.get("is_icd") else "main_port"
    destination_port_type = (
        "icd_port" if destination_location.get("is_icd") else "main_port"
    )
    port_pair_type = f"{origin_port_type}:{destination_port_type}"

    data = {
        "origin_port_id": str(request["origin_location_id"]),
        "destination_port_id": str(request["destination_location_id"]),
        "shipping_line_id": str(request["shipping_line_id"]),
        "port_pair_type": str(port_pair_type),
        "source": "chakravyuh",
    }

    return schedule_client.create_sailing_schedule_port_pair_coverage(data)