from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from playhouse.shortcuts import model_to_dict


POSSIBLE_DIRECT_FILTERS = ['location_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'specificity_type']

def get_eligible_fcl_freight_rate_free_day(request):
    if not all_fields_present(request):
        return {}

    query = query.select().where(FclFreightRateFreeDay.rate_not_available_entry == False,
                        FclFreightRateFreeDay.location_id == request['filters']['location_id'],
                        FclFreightRateFreeDay.trade_type == request['filters']['trade_type'],
                        FclFreightRateFreeDay.free_days_type == request['filters']['free_days_type'],
                        FclFreightRateFreeDay.container_size == request['filters']['container_size'],
                        FclFreightRateFreeDay.container_type == request['filters']['container_type'],
                        FclFreightRateFreeDay.shipping_line_id == request['filters']['shipping_line_id'],
                        FclFreightRateFreeDay.service_provider_id == request['filters']['service_provider_id'],
                        FclFreightRateFreeDay.specificity_type == request['filters']['specificity_type']
                      )

    if 'importer_exporter_id' in request['filters']:
      query = query.where(FclFreightRateFreeDay.importer_exporter_id == request['filters']['importer_exporter_id']) 

      # data = data.sort_by { |t| FclFreightRateConstants::LOCATION_HIERARCHY[t[:location_type]] }

      # data.first rescue nil

def all_fields_present(request):
    for field in (
        'location_id',
        'trade_type',
        'free_days_type',
        'container_size',
        'container_type',
        'shipping_line_id',
        'service_provider_id',
        'specificity_type'
    ):
        if field not in request:
            return False
    return True
