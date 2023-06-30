
from fastapi import HTTPException
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from micro_services.client import organization
from configs.haulage_freight_rate_constants import DEFAULT_RATE_TYPE

def create_audit(request, freight_id):

    audit_data = {}
    audit_data["validity_start"] = request.get("validity_start").isoformat()
    audit_data["validity_end"] = request.get("validity_end").isoformat()
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
        'cogo_entity_id': request.get('cogo_entity_id'),
        'shipping_line_id': request.get('shipping_line_id'),
        'transport_modes_keyword': '_'.join(transport_modes),
        'sourced_by_id': request.get('sourced_by_id'),
        'procured_by_id': request.get('procured_by_id'),
        'mode': request.get('mode', "manual"),
        'accuracy': request.get('accuracy', 100),
        'rate_type': request.get("rate_type", DEFAULT_RATE_TYPE)
    }

    init_key = f'{str(params.get("origin_location_id"))}:{str(params.get("destination_location_id"))}:{str(params.get("container_size"))}:{str(params.get("container_type"))}:{str(params.get("commodity", ""))}:{str(params.get("service_provider_id"))}:{str(params.get("shipping_line_id", ""))}:{str(params.get("haulage_type"))}:{str(params.get("transit_time", ""))}:{str(params.get("detention_free_time", ""))}:{str(params.get("trailer_type", ""))}:{str(params.get("trip_type", ""))}:{str(params.get("importer_exporter_id", ""))}:{str(params.get("cogo_entity_id", ""))}'
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

    haulage_freight_rate.validate_validity_object(haulage_freight_rate.validity_start,haulage_freight_rate.validity_end)

    haulage_freight_rate.set_platform_price()
    haulage_freight_rate.set_is_best_price()

    haulage_freight_rate.validate_before_save()
    
    try:
        haulage_freight_rate.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="rate not saved")

    haulage_freight_rate.update_line_item_messages(haulage_freight_rate.possible_charge_codes())

    if not haulage_freight_rate.importer_exporter_id:
        haulage_freight_rate.delete_rate_not_available_entry()

    create_audit(request, haulage_freight_rate.id)

    haulage_freight_rate.update_platform_prices_for_other_service_providers()

    delay_haulage_functions.apply_async(kwargs={'haulage_object':haulage_freight_rate,'request':request},queue='low')
    
    if request.get('haulage_freight_rate_request_id'):
        update_haulage_freight_rate_request_in_delay({'haulage_freight_rate_request_id': request.get('haulage_freight_rate_request_id'), 'closing_remarks': 'rate_added', 'performed_by_id': request.get('performed_by_id')})
    
    return {"id": haulage_freight_rate.id}
