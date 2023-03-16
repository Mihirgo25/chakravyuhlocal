from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge

def get_fcl_freight_rate_commodity_surcharge(request):
    if not all_fields_present(request):
        return {}
    objects = find_object(request)
    
    if not objects:
        return {} 

    objects.detail()
    return objects

def all_fields_present(request):
    if request.origin_location_id and request.destination_location_id and request.container_size and request.container_type and request.commodity and request.shipping_line_id and request.service_provider_id:
        return True
    else:
        return False

def find_object(request):
    objects = FclFreightRateCommoditySurcharge.select().where(
        FclFreightRateCommoditySurcharge.origin_location_id == request.origin_location_id,
        FclFreightRateCommoditySurcharge.destination_location_id == request.destination_location_id,
        FclFreightRateCommoditySurcharge.container_size == request.container_size,
        FclFreightRateCommoditySurcharge.container_type == request.container_type,
        FclFreightRateCommoditySurcharge.commodity == request.commodity,
        FclFreightRateCommoditySurcharge.shipping_line_id == request.shipping_line_id,
        FclFreightRateCommoditySurcharge.service_provider_id == request.service_provider_id
    ).dicts().get()

    return objects