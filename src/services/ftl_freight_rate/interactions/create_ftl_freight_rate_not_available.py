from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from database.rails_db import get_eligible_orgs
from configs.ftl_freight_rate_constants import DEFAULT_RATE_TYPE

def create_ftl_freight_rate_not_available(request):
    service_provider_query = FtlFreightRate.select(FtlFreightRate.service_provider_id).distinct().where(
        FtlFreightRate.origin_location_id == request.get('origin_location_id'),
        FtlFreightRate.destination_location_id == request.get('destination_location_id'),
        FtlFreightRate.truck_type == request.get('truck_type'),
        FtlFreightRate.commodity == request.get('commodity'),
        FtlFreightRate.rate_type == DEFAULT_RATE_TYPE,
        FtlFreightRate.importer_exporter_id == None
    ).dicts()
      
    present_service_provider_ids = []
    for id in service_provider_query:
        present_service_provider_ids.append(id['service_provider_id'])
    
    find_service_provider_ids = find_service_providers()

    for service_provider_id in list(set(find_service_provider_ids).difference(set(present_service_provider_ids))):
        FtlFreightRate.create(
            origin_location_id = request['origin_location_id'],
            destination_location_id = request['destination_location_id'],
            truck_type = request['truck_type'],
            commodity = request['commodity'],
            service_provider_id = service_provider_id,
            rate_not_available_entry = True)
        
    return True

def find_service_providers():
    service_provider_ids = get_eligible_orgs('ftl_freight')
    return service_provider_ids
