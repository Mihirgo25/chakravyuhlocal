from services.fcl_freight_rate.models.critical_port_trend_indexes import CriticalPortTrendIndex
from libs.get_multiple_service_objects import get_multiple_service_objects
from database.db_session import db
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from fastapi import HTTPException

def create_audit(request, index_id):
    audit_data = {
        "origin_port_id": request["origin_port_id"],
        "destination_port_id": request["destination_port_id"],
        "min_allowed_percentage_change": request["min_allowed_percentage_change"],
        "max_allowed_percentage_change": request["max_allowed_percentage_change"],
        "min_allowed_markup": request["min_allowed_markup"],
        "max_allowed_markup": request["max_allowed_markup"],
        "manual_gri": request.get("manual_gri"),
        "approval_status": request.get("approval_status"),
        }
    
    try:
        FclServiceAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        rate_sheet_id = request.get('rate_sheet_id'),
        data = audit_data,
        object_id = index_id,
        object_type = 'CriticalPortTrendIndex'
      )
        
    except:
      raise HTTPException(status_code=500, detail='fcl freight audit did not save')

def create_critical_port_trend_index(request):
    object_type = 'Critical_Port_Trend_Index'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request_data):
    create_params = {
        "origin_port_id": request_data["origin_port_id"],
        "destination_port_id": request_data["destination_port_id"],
        "min_allowed_percentage_change": request_data["min_allowed_percentage_change"],
        "max_allowed_percentage_change": request_data["max_allowed_percentage_change"],
        "min_allowed_markup": request_data["min_allowed_markup"],
        "max_allowed_markup": request_data["max_allowed_markup"],
        "manual_gri": request_data.get("manual_gri"),
        "approval_status": request_data.get("approval_status"),
        "performed_by_id": request_data.get("performed_by_id"),
        "performed_by_type": request_data.get("performed_by_type"),
    }

    index_object = CriticalPortTrendIndex(**create_params)
    get_multiple_service_objects(index_object)
    create_audit(request_data, str(index_object.id))
    index_object.set_locations()
    index_object.save()

    return {'id': str(index_object.id)}
