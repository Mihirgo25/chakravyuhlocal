from micro_services.client import maps
from database.db_session import rd
from database.rails_db import get_organization

LOCATION_IDS = ['origin_port_id','destination_port_id','origin_airport_id','destination_airport_id']

def add_service_objects(results):
    location_ids = set()
    shipping_line_ids = set()
    service_provider_ids = set()

    for result in results:
        for k,v in result.items():
            if k in LOCATION_IDS:
                location_ids.add(v)
            if k == ['shipping_line_id','airline_id']:
                shipping_line_ids.add(v)
            if k == ['service_provider_id']:
                service_provider_ids.add(v)

    locations =  get_locations(location_ids)
    shipping_lines = get_shipping_lines(shipping_line_ids)
    service_provider = get_service_providers(service_provider_ids)

    for result in results:
        update_results = dict()
        for k, v in result.items():
            if k in LOCATION_IDS:
                location = locations.get(v)
                if not location:
                    continue
                update_results[f"{k[:-3]}"] = location['name']
            if k == ['shipping_line_id','airline_id']:
                shipping_line = shipping_lines.get(v)
                if not shipping_line:
                    continue
                update_results[f"{k[:-3]}"] = shipping_line
            if k == ['service_provider_id']:
                service_provider = service_provider.get(v)
                if not service_provider:
                    continue
                update_results[f"{k[:-3]}"] = service_provider
        result.update(update_results)

async def get_shipping_lines(ids):
    shipping_lines_data = maps.list_operators(dict(filters=dict(id=list(ids)),page_limit=len(ids)))
    shipping_lines = shipping_lines_data['list']
    return {
        shipping_line["id"]: shipping_line for shipping_line in shipping_lines
    }

def get_locations(ids):
    locations_data = maps.list_locations(dict(filters=dict(id=list(ids)),
                includes=dict(id=True, name=True,port_code = True),
                page_limit=len(ids)))
    locations = locations_data['list']
    return {
        location["id"]: location for location in locations
    }

def get_service_providers(ids):
    service_provider_data = get_organization(id=list(ids))
    return {
        service_provider['id']: service_provider for service_provider in service_provider_data
    }