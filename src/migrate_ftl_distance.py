from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from micro_services.client  import maps
from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import get_road_distance

def update_region_id():
    all_rates = FtlFreightRate.select()

    for ftl_rate in all_rates:
        ids = [str(ftl_rate.origin_location_id), str(ftl_rate.destination_location_id)]
        locations_response = maps.list_locations({'filters':{"id": ids}, 'includes': {'id': True, 'region_id': True}})
        locations = []
        if 'list' in locations_response:
            locations = locations_response["list"]
        for location in locations:
            if str(location['id']) == str(ftl_rate.origin_location_id):
                ftl_rate.origin_region_id = location.get('region_id')
            if str(location['id']) == str(ftl_rate.destination_location_id):
                ftl_rate.destination_region_id = location.get('region_id')
        
        ftl_rate.save()

    print("REGION IDS UPDATED")

def update_distance():
    all_rates = FtlFreightRate.select()

    for ftl_rate in all_rates:
        distance = get_road_distance(ftl_rate.origin_location_id, ftl_rate.destination_location_id)
        ftl_rate.distance = distance
        ftl_rate.save()

    print("DISTANCE UPDATED")
        