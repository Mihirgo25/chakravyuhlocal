from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize


def create_audit(request, commodity_surcharge):

    audit_data = {}
    audit_data['price'] = request['price']
    audit_data['currency'] = request['currency']
    audit_data['remarks'] = request.get('remarks')

    FclFreightRateAudit.create(
        action_name = 'create',
        rate_sheet_id = request.get('rate_sheet_id'),
        performed_by_id = request['performed_by_id'],
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data
    )

def create_fcl_freight_rate_commodity_surcharge(request):
    row = {
        'origin_location_id' : request.get("origin_location_id"),
        'destination_location_id' : request.get("destination_location_id"),
        'container_size' : request.get("container_size"),
        'container_type' : request.get("container_type"),
        'commodity' : request.get("commodity"),
        'shipping_line_id' : request.get("shipping_line_id"),
        'service_provider_id' : request.get("service_provider_id"),
        }
    commodity_surcharge = find_or_initialize(FclFreightRateCommoditySurcharge,**row)

    for k, v in request.items():
        if k in ['price', 'currency', 'remarks']:
            setattr(commodity_surcharge, k, v)
    commodity_surcharge.validate()

    if not commodity_surcharge.save():
        raise HTTPException(status_code=422, detail="Commodity Surcharge not saved")
    
    commodity_surcharge.update_freight_objects()

    create_audit(request, commodity_surcharge.id)

    return {
      id: commodity_surcharge.id
    }