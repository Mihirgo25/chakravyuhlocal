from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit


def find_or_initialize(**kwargs):
    try:
        obj = FclFreightRateSeasonalSurcharge.get(**kwargs)
    except FclFreightRateSeasonalSurcharge.DoesNotExist:
        obj = FclFreightRateSeasonalSurcharge(**kwargs)
    return obj

def create_audit(request, seasonal_surcharge_id):

    audit_data = {}
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()
    audit_data['price'] = request['price']
    audit_data['currency'] = request['currency']
    audit_data['remarks'] = request.get('remarks')

    FclFreightRateAudit.create(
        rate_sheet_id = request.get('rate_sheet_id'),
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data,
    )

def create_fcl_freight_rate_seasonal_surcharge(request):
    row = {
        'origin_port_id' : request.get("origin_location_id"),
        'destination_port_id' : request.get("destination_location_id"),
        'container_size' : request.get("container_size"),
        'container_type' : request.get("container_type"),
        'shipping_line_id' : request.get("shipping_line_id"),
        'service_provider_id' : request.get("service_provider_id"),
        'code' : request.get("code")
        }

    seasonal_surcharge = find_or_initialize(**row)
    seasonal_surcharge.__dict__.update({k: v for k, v in request.items() if k in ['price', 'currency', 'validity_start', 'validity_end', 'remarks']})

    if not seasonal_surcharge.save():
        raise HTTPException(status_code=422, detail="Seasonal Surcharge not saved")
    
    seasonal_surcharge.update_freight_objects()

    create_audit(request, seasonal_surcharge.id)

    return {
      id: seasonal_surcharge.id
    }
