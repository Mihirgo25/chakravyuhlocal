from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate

def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRate.get(**kwargs)
  except FclFreightRate.DoesNotExist:
    obj = FclFreightRate(**kwargs)
  return obj

def create_fcl_freight_rate(request):
  row = {
    'origin_port_id' : request.origin_port_id,
    'origin_main_port_id' : request.origin_main_port_id,
    'destination_port_id' : request.destination_port_id,
    'destination_main_port_id' : request.destination_main_port_id,
    'container_size' : request.container_size,
    'container_type' : request.container_type,
    'commodity' : request.commodity,
    'shipping_line_id' : request.shipping_line_id,
    'service_provider_id' : request.service_provider_id,
    'importer_exporter_id' : request.importer_exporter_id,
    'rate_not_available_entry' : false
  }

  freight = find_or_initialize(**row)

  freight.weight_limit = request.weight_limit
  freight.origin_local = freight.origin_local.json().update(request.origin_local)
  freight.destination_local = freight.destination_local.json().update(request.destination_local)

  freight.validate_validity_object(request.validity_start, request.validity_end)
  freight.validate_line_items(request.line_items)

  if freight.errors:
    return freight.errors

  freight.set_validities(request.validity_start, request.validity_end, request.line_items, request.schedule_type, false, request.payment_term)
  freight.set_platform_prices
  freight.set_is_best_price
  freight.set_last_rate_available_date


  try:
    freight.save()
  except:
    return freight.errors()

  if request.importer_exporter_id is None:
    freight.delete_rate_not_available_entry
  
  
  


  return {"id": query.id}