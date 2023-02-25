from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay


POSSIBLE_DIRECT_FILTERS = ['location_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'specificity_type']

def get_eligible_fcl_freight_rate_free_day(request):

    if all_fields_present(request):
        query = FclFreightRateFreeDay.select().where(FclFreightRateFreeDay.rate_not_available_entry == False)
        print('query1', query)
        query = query.where(FclFreightRateFreeDay.location_id == request['filters']['location_id'],
                            FclFreightRateFreeDay.trade_type == request['filters']['trade_type'],
                            FclFreightRateFreeDay.free_days_type == request['filters']['free_days_type'],
                            FclFreightRateFreeDay.container_size == request['filters']['container_size'],
                            FclFreightRateFreeDay.container_type == request['filters']['container_type'],
                            FclFreightRateFreeDay.shipping_line_id == request['filters']['shipping_line_id'],
                            FclFreightRateFreeDay.service_provider_id == request['filters']['service_provider_id'],
                            FclFreightRateFreeDay.specificity_type == request['filters']['specificity_type']
                          )
        print('query2', query)

        if 'importer_exporter_id' in request['filters']:
          query = query.where(FclFreightRateFreeDay.importer_exporter_id == request['filters']['importer_exporter_id']) 

        print('query3',query)

      # data = query.as_json.map(&:deep_symbolize_keys)

      # data = data.sort_by { |t| FclFreightRateConstants::LOCATION_HIERARCHY[t[:location_type]] }

      # data.first rescue nil
    return {}

def all_fields_present(request):
    if ('location_id' in request['filters']) and ('trade_type' in request['filters']) and ('free_days_type' in request['filters']) and ('container_size' in request['filters']) and ('container_type' in request['filters']) and ('shipping_line_id' in request['filters']) and ('service_provider_id' in request['filters']) and ('specificity_type' in request['filters']):
        return True
    return False
