from fastapi import HTTPException
from database.db_session import db
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from configs.ftl_freight_rate_constants import DEFAULT_RATE_TYPE
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate

def create_audit(request, freight_id):
    audit_data = {}
    audit_data["validity_start"] = request.get("validity_start").isoformat()
    audit_data["validity_end"] = request.get("validity_end").isoformat()
    audit_data["line_items"] = request.get("line_items")
    audit_data["Ftl_freight_rate_request_id"] = request.get("Ftl_freight_rate_request_id")

    audit_id = FtlFreightRateAudit.create(
        rate_sheet_id=request.get("rate_sheet_id"),
        action_name="create",
        performed_by_id=request["performed_by_id"],
        data=audit_data,
        object_id=freight_id,
        object_type="FtlFreightRate",
        source=request.get("source"),
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id = request.get('procured_by_id')
    )
    return audit_id

def create_ftl_freight_rate(request):
    with db.atomic():
      return execute_transaction_code(request)
  
def execute_transaction_code(request):
    from celery_worker import delay_ftl_functions, update_ftl_freight_rate_request_delay

    params = {
      'rate_sheet_id':request.get('rate_sheet_id'),
      'origin_location_id':request.get('origin_location_id'),
      'destination_location_id':request.get('destination_location_id'),
      'truck_type':request.get('truck_type'),
      'commodity':request.get('commodity'),
      'importer_exporter_id':request.get('importer_exporter_id'),
      'service_provider_id':request.get('service_provider_id'),
      'performed_by_id':request.get('performed_by_id'),
      'procured_by_id':request.get('procured_by_id'),
      'sourced_by_id':request.get('sourced_by_id'),
      'validity_start':request.get('validity_start'),
      'validity_end':request.get('validity_end'),
      'truck_body_type':request.get('truck_body_type'),
      'trip_type':request.get('trip_type'),
      'transit_time':request.get('transit_time'),
      'detention_free_time':request.get('detention_free_time'),
      'minimum_chargeable_weight':request.get('minimum_chargeable_weight'),
      'unit':request.get('unit'),
      'line_items':request.get('line_items'),
      'ftl_freight_rate_request_id':request.get('ftl_freight_rate_request_id'),
      'mode': request.get('mode', "manual"),
      'accuracy': request.get('accuracy', 100),
      'rate_type': request.get("rate_type", DEFAULT_RATE_TYPE)
  }

    init_key = f'{str(params["origin_location_id"])}:{str(params["destination_location_id"])}:{str(params["truck_type"])}:{str(params["commodity"] or "")}:{str(params["service_provider_id"])}:{str(params["importer_exporter_id"] or "")}:{str(params["truck_body_type"])}'

    ftl_freight_rate = (
        FtlFreightRate.select().where(
        FtlFreightRate.init_key == init_key,
        FtlFreightRate.rate_type == params["rate_type"],
        ).first()
      )
  
    if not ftl_freight_rate:
      ftl_freight_rate = FtlFreightRate(init_key = init_key)
      for key in list(params.keys()):
          setattr(ftl_freight_rate, key, params[key])

    ftl_freight_rate.set_locations()

    ftl_freight_rate.validate_validities(ftl_freight_rate.validity_start, ftl_freight_rate.validity_end)
    ftl_freight_rate.rate_not_available_entry = False

    ftl_freight_rate.set_platform_price()
    ftl_freight_rate.set_is_best_price()

    try:
      ftl_freight_rate.save()
    except Exception as e:
      raise HTTPException(status_code=400, detail="rate not saved")
    
    ftl_freight_rate.update_line_item_messages(ftl_freight_rate.possible_charge_codes())

    if not ftl_freight_rate.importer_exporter_id:
        ftl_freight_rate.delete_rate_not_available_entry()

    create_audit(request, ftl_freight_rate.id)

    ftl_freight_rate.update_platform_prices_for_other_service_providers()
    
    delay_ftl_functions.apply_async(kwargs={'ftl_object':ftl_freight_rate,'request':request},queue='low')

    if request.get('ftl_freight_rate_request_id'):
      update_ftl_freight_rate_request_delay.apply_async(kwargs={'request':{'ftl_freight_rate_request_id': request.get('ftl_freight_rate_request_id'), 'closing_remarks': 'rate_added', 'performed_by_id': request.get('performed_by_id')}},queue='low')
    
    return {"id": ftl_freight_rate.id}
