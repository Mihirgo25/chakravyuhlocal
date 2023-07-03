from fastapi import HTTPException
from database.db_session import db
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit
from configs.ftl_freight_rate_constants import DEFAULT_RATE_TYPE


def create_ftl_freight_rate(request):
  with db.atomic():
    return execute_transaction_code(request)
  
def execute_transaction_code(request):
   request = { key: value for key, value in request.items() if value }
   row = {
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
        'ftl_freight_rate_request_id':request.get('ftl_freight_rate_request_id'),
        "rate_type": request.get("rate_type", DEFAULT_RATE_TYPE)
    }
   
  
