
from fastapi import HTTPException
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from micro_services.client import organization
from celery_worker import update_haulage_freight_rate_request_in_delay
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from configs.haulage_freight_rate_constants import DEFAULT_RATE_TYPE
from celery_worker import delay_haulage_functions

def create_audit(request, freight_id):

    audit_data = {}
    audit_data["validity_start"] = request.get("validity_start")
    audit_data["validity_end"] = request.get("validity_end")
    audit_data["line_items"] = request.get("line_items")
    audit_data["haulage_freight_rate_request_id"] = request.get("haulage_freight_rate_request_id")

    audit_id = HaulageFreightRateAudit.create(
        rate_sheet_id=request.get("rate_sheet_id"),
        action_name="create",
        performed_by_id=request["performed_by_id"],
        data=audit_data,
        object_id=freight_id,
        object_type="HaulageFreightRate",
        source=request.get("source")
    )
    return audit_id

def create_haulage_freight_rate(request):
    from celery_worker import delay_haulage_functions, update_haulage_freight_rate_request_in_delay

    transport_modes = request.get('transport_modes',[])
    transport_modes = set(transport_modes)
    transport_modes = list(transport_modes)
    transport_modes.sort()
    params = get_haulage_unique_params(request)
    haulage_freight_rate = HaulageFreightRate.select().where(
        HaulageFreightRate.origin_location_id == request.get('origin_location_id'),
        HaulageFreightRate.destination_location_id == request.get('destination_location_id'),
        HaulageFreightRate.container_size== request.get('container_size'),
        HaulageFreightRate.container_type== request.get('container_type'),
        HaulageFreightRate.commodity == request.get('commodity'),
        HaulageFreightRate.service_provider_id==request.get('service_provider_id'),
        HaulageFreightRate.haulage_type == request.get('haulage_type'),
        HaulageFreightRate.transit_time == request.get('transit_time'),
        HaulageFreightRate.detention_free_time == request.get('detention_free_time'),
        HaulageFreightRate.trip_type == request.get('trip_type'),
        HaulageFreightRate.importer_exporter_id == request.get('importer_exporter_id'),
        HaulageFreightRate.shipping_line_id == request.get('shipping_line_id'),
        HaulageFreightRate.transport_modes_keyword == '_'.join(transport_modes)).first()
    
    if not haulage_freight_rate:
        haulage_freight_rate = HaulageFreightRate(**params)

    haulage_freight_rate.line_items = request.get('line_items')
    haulage_freight_rate.transport_modes = request.get('transport_modes')
    haulage_freight_rate.validity_start = request.get('validity_start')
    haulage_freight_rate.validity_end = request.get('validity_end')

    possible_charge_codes = haulage_freight_rate.possible_charge_codes()
    mandatory_charge_codes = haulage_freight_rate.mandatory_charge_codes(possible_charge_codes)
    haulage_freight_rate.validate_validity_object(haulage_freight_rate.validity_start,haulage_freight_rate.validity_end)
    haulage_freight_rate.set_platform_price()
    haulage_freight_rate.update_line_item_messages(haulage_freight_rate.possible_charge_codes())

    if not haulage_freight_rate.importer_exporter_id:
        haulage_freight_rate.delete_rate_not_available_entry()

    audit_params = get_audit_params(request)

    audit_entry = HaulageFreightRateAudit(**audit_params)
    if not HaulageFreightRate.select().where(HaulageFreightRate.service_provider_id==request["service_provider_id"], HaulageFreightRate.rate_not_available_entry==False).exists():
            organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})


    haulage_freight_rate.update_platform_prices_for_other_service_providers()
    
    if request.get('haulage_freight_rate_request_id'):
        update_haulage_freight_rate_request_in_delay({'haulage_freight_rate_request_id': request.get('haulage_freight_rate_request_id'), 'closing_remarks': 'rate_added', 'performed_by_id': request.get('performed_by_id')})

    get_multiple_service_objects(haulage_freight_rate)

    if haulage_freight_rate.validate_before_save():
            haulage_freight_rate.save()
    
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
        'transport_modes_keyword': '_'.join(transport_modes),
        'mode': request.get('mode', "manual"),
        'accuracy': request.get('accuracy', 100),
        'rate_type': request.get("rate_type", DEFAULT_RATE_TYPE)
    }

    init_key = f'{str(params["origin_location_id"])}:{str(params["destination_location_id"])}:{str(params["container_size"])}:{str(params["container_type"])}:{str(params["commodity"] or "")}:{str(params["service_provider_id"])}:{str(params["shipping_line_id"] or "")}:{str(params["haulage_type"])}:{str(params["trailer_type"] or "")}:{str(params["trip_type"] or "")}:{str(params["importer_exporter_id"] or "")}'
    haulage_freight_rate = (
        HaulageFreightRate.select().where(
        HaulageFreightRate.init_key == init_key,
        HaulageFreightRate.rate_type == params["rate_type"]
        ).first()
    )
    
    
    if not haulage_freight_rate:
        haulage_freight_rate = HaulageFreightRate(init_key = init_key)
        for key in list(params.keys()):
            setattr(haulage_freight_rate, key, params[key])

    haulage_freight_rate.set_locations()

    haulage_freight_rate.line_items = request.get('line_items')
    haulage_freight_rate.transport_modes = request.get('transport_modes')
    haulage_freight_rate.validity_start = request.get('validity_start')
    haulage_freight_rate.validity_end = request.get('validity_end')
    haulage_freight_rate.procured_by_id = request.get('procured_by_id')
    haulage_freight_rate.sourced_by_id = request.get('sourced_by_id')
    
    haulage_freight_rate.validate_validity_object(haulage_freight_rate.validity_start,haulage_freight_rate.validity_end)

    haulage_freight_rate.set_platform_price()
    haulage_freight_rate.set_is_best_price()
    haulage_freight_rate.rate_not_available_entry = False

    haulage_freight_rate.validate_before_save()
    haulage_freight_rate.update_line_item_messages(haulage_freight_rate.possible_charge_codes())

    try:
        haulage_freight_rate.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="rate not saved")

    if not haulage_freight_rate.importer_exporter_id:
        haulage_freight_rate.delete_rate_not_available_entry()

    create_audit(request, haulage_freight_rate.id)

    haulage_freight_rate.update_platform_prices_for_other_service_providers()

    delay_haulage_functions.apply_async(kwargs={'haulage_object':haulage_freight_rate,'request':request},queue='low')
    
    if request.get('haulage_freight_rate_request_id'):
        update_haulage_freight_rate_request_in_delay({'haulage_freight_rate_request_id': request.get('haulage_freight_rate_request_id'), 'closing_remarks': 'rate_added', 'performed_by_id': request.get('performed_by_id')})
    
    return {"id": haulage_freight_rate.id}
