from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
import yaml

def get_fcl_freight_rate_seasonal_surcharge(request):
    with open('/Users/user/Desktop/ocean-rms/src/configs/charges/fcl_freight_seasonal_charges.yml', 'r') as file:
        fcl_freight_seasonal_charges = yaml.safe_load(file)
    
    if not all_fields_present(request):
        return {'seasonal_surcharge_charge_codes': fcl_freight_seasonal_charges} 

    try:
        detail = find_object(request).detail 
    except:
        detail = {}

    return detail | {'seasonal_surcharge_charge_codes': fcl_freight_seasonal_charges}


def all_fields_present(request):
    if request.origin_location_id and request.destination_location_id and  request.container_size and  request.container_type and  request.code and request.shipping_line_id and  request.service_provider_id:
        return True
    else:
        return False

def find_object(request):
    objects = FclFreightRateSeasonalSurcharge.select().where(
        FclFreightRateSeasonalSurcharge.origin_location_id == request.origin_location_id,
        FclFreightRateSeasonalSurcharge.destination_location_id == request.destination_location_id,
        FclFreightRateSeasonalSurcharge.container_size == request.container_size,
        FclFreightRateSeasonalSurcharge.container_type == request.container_type,
        FclFreightRateSeasonalSurcharge.code == request.code,
        FclFreightRateSeasonalSurcharge.shipping_line_id == request.shipping_line_id,
        FclFreightRateSeasonalSurcharge.service_provider_id == request.service_provider_id
    ).dicts().get()

    return objects