
from fastapi import HTTPException
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_audits import HaulageFreightRateAudit
from micro_services.client import organization
from celery_worker import update_haulage_freight_rate_request_in_delay
def create_haulage_freight_rate(request):

    transport_modes = request.get('transport_modes',[])
    transport_modes = set(transport_modes)
    transport_modes = list(transport_modes)
    transport_modes.sort()
    params = get_haulage_unique_params(request)
    haulage_freight_rate = HaulageFreightRate.select().where(
        HaulageFreightRate.origin_location_id == request.get('location_id'),
        HaulageFreightRate.destination_location_id ==request.get('trade_type'),
        HaulageFreightRate.container_size== request.get('container_size'),
        HaulageFreightRate.container_type==request.get('container_type'),
        HaulageFreightRate.commodity == request.get('commodity'),
        HaulageFreightRate.service_provider_id==request.get('service_provider_id'),
        HaulageFreightRate.haulage_type == request.get('haulage_type'),
        # HaulageFreightRate.trailer_type == request.get('trailer_type'))
        HaulageFreightRate.transit_time == request.get('transit_time'),
        HaulageFreightRate.detention_free_time == request.get('detention_free_time'),
        HaulageFreightRate.trip_type == request.get('trip_type'),
        HaulageFreightRate.importer_exporter_id == request.get('importer_exporter_id'),
        HaulageFreightRate.shipping_line_id == request.get('shipping_line_id'),
        HaulageFreightRate.transport_modes_keyword == '_'.join(transport_modes))
    
    if not haulage_freight_rate:
        haulage_freight_rate = HaulageFreightRate(**params)

    haulage_freight_rate.line_items = request.get('line_items')
    haulage_freight_rate.transport_modes = request.get('transport_modes')
    haulage_freight_rate.validity_start = request.get('validity_start')
    haulage_freight_rate.validity_end = request.get('validity_end')

    possible_charge_codes = haulage_freight_rate.possible_charge_codes()
    mandatory_charge_codes = haulage_freight_rate.mandatory_charge_codes(possible_charge_codes)
    haulage_freight_rate.validate_validity_object(haulage_freight_rate.validity_start,haulage_freight_rate.validity_end)
    haulage_freight_rate.set_platform_price(haulage_freight_rate.mandatory_charge_codes(haulage_freight_rate.possible_charge_codes()),currency = 'INR')
    haulage_freight_rate.update_line_item_messages(haulage_freight_rate.possible_charge_codes())

    if not haulage_freight_rate.importer_exporter_id:
        haulage_freight_rate.delete_rate_not_available_entry()

    audit_params = get_audit_params(request)

    audit_entry = HaulageFreightRateAudit(**audit_params)
    if not HaulageFreightRate.select().where(HaulageFreightRate.service_provider_id==request["service_provider_id"], HaulageFreightRate.rate_not_available_entry==False).exists():
            organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})


    haulage_freight_rate.update_platform_prices_for_other_service_providers()
    
    if request.get('fcl_freight_rate_request_id'):
        update_haulage_freight_rate_request_in_delay({'haulage_freight_rate_request_id': request.get('haulage_freight_rate_request_id'), 'closing_remarks': 'rate_added', 'performed_by_id': request.get('performed_by_id')})

    try:
        haulage_freight_rate.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="rate did not save")
    return {"id": haulage_freight_rate.id}

    





def get_audit_params(request):
    audit_data = {
        'line_items' : request.get('line_items')
    }
    
    return {
      'action_name': 'create',
      'performed_by_id': request.get('performed_by_id'),
      'rate_sheet_id': request.get('rate_sheet_id'),
      'procured_by_id': request.get('procured_by_id'),
      'sourced_by_id': request.get('sourced_by_id'),
      'data': audit_data
    }

def get_haulage_unique_params(request):
    transport_modes = request.get('transport_modes',[])
    transport_modes = set(transport_modes)
    transport_modes = list(transport_modes)
    transport_modes.sort()
    params = {
        'origin_location_id' : request.get('origin_location_id'),
        'destination_location_id': request.get('destination_location_id'),
        'container_size': request.get('container_size'),
        'container_type': request.get('container_type'),
        'commodity': request.get('commodity'),
        'service_provider_id' : request.get('service_provider_id'),
        'haulage_type': request.get('haulage_type'),
        'trailer_type': request.get('trailer_type'),
        'transit_time': request.get('transit_time'),
        'detention_free_time': request.get('detention_free_time'),
        'trip_type': request.get('trip_type'),
        'commodity': request.get('commodity'),
        'importer_exporter_id': request.get('importer_exporter_id'),
        'shipping_line_id': request.get('shipping_line_id'),
        'transport_modes_keyword': '_'.join(transport_modes)
    }

    return params


