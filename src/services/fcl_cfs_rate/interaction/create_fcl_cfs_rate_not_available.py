from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from micro_services.client import organization
from playhouse.shortcuts import model_to_dict


def find_service_provider_ids(request):
    service_provider_ids = organization.get_eligible_service_organizations({
    'service': 'fcl_cfs',
    'data': {
        'location_id': request['location_id'],
        'country_id': request['country_id'],
        'trade_type': request['trade_type'],
        'container_size': request['container_size'],
        'container_type': request['container_type'],
        'commodity': request['commodity']
    }
    })['ids']

    return service_provider_ids

def create_fcl_cfs_rate_not_available(request):
    present_service_provider_data = (
        FclCfsRate.select(FclCfsRate.service_provider_id)
        .where(
            (FclCfsRate.location_id == request["location_id"]) &
            (FclCfsRate.trade_type == request["trade_type"]) &
            (FclCfsRate.container_size == request["container_size"]) &
            (FclCfsRate.container_type == request["container_type"]) &
            (FclCfsRate.commodity == request["commodity"]) &
            (FclCfsRate.importer_exporter_id.is_null(True))
        )
        .distinct()
    )
    present_service_provider_ids = [model_to_dict(item)['service_provider_id'] for item in present_service_provider_data.execute()]
    missing_service_provider_ids = list(set(find_service_provider_ids(request)).difference(set(present_service_provider_ids)))

    for service_provider_id in missing_service_provider_ids:
        FclCfsRate.create(
            location_id=request["location_id"],
            trade_type=request["trade_type"],
            container_size=request["container_size"],
            container_type=request["container_type"],
            commodity=request["commodity"],
            service_provider_id=service_provider_id,
            rate_not_available_entry=True,
            line_items=[]
        )

    return True

