from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from playhouse.shortcuts import model_to_dict
from configs.fcl_freight_rate_constants import LOCATION_HIERARCHY

possible_direct_filters = ['location_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id', 'local_service_provider_ids', 'importer_exporter_id', 'specificity_type','free_limit', 'validity_start', 'validity_end']

def get_eligible_fcl_freight_rate_free_day(request):
    if not all_fields_present(request):
        return {}

    query = FclFreightRateFreeDay.select().where(FclFreightRateFreeDay.rate_not_available_entry == False,
                        FclFreightRateFreeDay.location_id == request['filters']['location_id'],
                        FclFreightRateFreeDay.trade_type == request['filters']['trade_type'],
                        FclFreightRateFreeDay.free_days_type == request['filters']['free_days_type'],
                        FclFreightRateFreeDay.container_size == request['filters']['container_size'],
                        FclFreightRateFreeDay.container_type == request['filters']['container_type'],
                        FclFreightRateFreeDay.shipping_line_id == request['filters']['shipping_line_id'],
                        FclFreightRateFreeDay.service_provider_id in list(set(request['filters'].get('service_provider_id', []) + request['filters'].get('local_service_provider_ids', []))),
                        FclFreightRateFreeDay.specificity_type == request['filters']['specificity_type']
                      )

    if 'importer_exporter_id' in request['filters']:
        query = query.where(FclFreightRateFreeDay.importer_exporter_id == request['filters']['importer_exporter_id'])

    if 'free_limit' in request['filters']:
        query = query.where(FclFreightRateFreeDay.free_limit == request['filters']['free_limit'])

    if 'validity_start' in request['filters'] and 'validity_end' in request['filters']:
        query = query.where(FclFreightRateFreeDay.validity_start <= request['filters']['validity_start'] and FclFreightRateFreeDay.validity_end >= request['filters']['validity_end'])

    data = [model_to_dict(item) for item in query.execute()]
    data = sorted(data, key=lambda t:LOCATION_HIERARCHY[t['location_type']])
    data = data[0] if data else {}
    # if not request['sort_by_specificity_type']:
    #     data = sorted(data, key=lambda t: [
    #         LOCATION_HIERARCHY[t['location_type']],
    #         0 if request['filters'].get('service_provider_id') == t['service_provider_id'] else 1,
    #         0 if t['specificity_type'] == 'shipping_line' else 1 if t['specificity_type'] == 'cogoport' else 2
    #     ])
    # else:
    #     data = sorted(data, key=lambda t: [
    #         0 if t['specificity_type'] == 'rate_specific' else 1 if t['specificity_type'] == 'shipping_line' else 2
    #     ])

    # data = data[0] if data else None

    return data

def all_fields_present(request):
    for field in (
        'location_id',
        'trade_type',
        'free_days_type',
        'container_size',
        'container_type',
        'shipping_line_id'
    ):
        if field not in request['filters']:
            return False
    return True
