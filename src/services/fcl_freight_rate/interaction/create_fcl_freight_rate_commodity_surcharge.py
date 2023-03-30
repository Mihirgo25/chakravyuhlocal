from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from celery_worker import update_multiple_service_objects,update_freight_objects_for_commodity_surcharge
def create_audit(request, commodity_surcharge_id):

    audit_data = {}
    audit_data['price'] = request['price']
    audit_data['currency'] = request['currency']
    audit_data['remarks'] = request.get('remarks')
    FclServiceAudit.create(
        action_name = 'create',
        rate_sheet_id = request.get('rate_sheet_id'),
        performed_by_id = request['performed_by_id'],
        data = audit_data,
        object_id = commodity_surcharge_id,
        object_type = 'FclFreightRateCommoditySurcharge'
    )

def create_fcl_freight_rate_commodity_surcharge(request):
    object_type = 'Fcl_Freight_Rate_Commodity_Surcharge'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)

    with db.atomic() as transaction:
        try:
          return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    row = {
        'origin_location_id' : request.get("origin_location_id"),
        'destination_location_id' : request.get("destination_location_id"),
        'container_size' : request.get("container_size"),
        'container_type' : request.get("container_type"),
        'commodity' : request.get("commodity"),
        'shipping_line_id' : request.get("shipping_line_id"),
        'service_provider_id' : request.get("service_provider_id")
        }

    commodity_surcharge = FclFreightRateCommoditySurcharge.select().where(
        FclFreightRateCommoditySurcharge.origin_location_id == request.get("origin_location_id"),
        FclFreightRateCommoditySurcharge.destination_location_id == request.get("destination_location_id"),
        FclFreightRateCommoditySurcharge.container_size == request.get("container_size"),
        FclFreightRateCommoditySurcharge.container_type == request.get("container_type"),
        FclFreightRateCommoditySurcharge.commodity == request.get("commodity"),
        FclFreightRateCommoditySurcharge.shipping_line_id == request.get("shipping_line_id"),
        FclFreightRateCommoditySurcharge.service_provider_id == request.get("service_provider_id")).first()

    if not commodity_surcharge:
        commodity_surcharge = FclFreightRateCommoditySurcharge(**row)

    for k, v in request.items():
        if k in ['price', 'currency', 'remarks']:
            setattr(commodity_surcharge, k, v)
    commodity_surcharge.validate()

    commodity_surcharge.sourced_by_id = request.get('sourced_by_id')
    commodity_surcharge.procured_by_id = request.get('procured_by_id')

    if not commodity_surcharge.save():
        raise HTTPException(status_code=500, detail="Commodity Surcharge not saved")
 
    update_freight_objects_for_commodity_surcharge.apply_async(kwargs={'surcharge_object':commodity_surcharge},queue='low')


    create_audit(request, commodity_surcharge.id)

    update_multiple_service_objects.apply_async(kwargs={'object':commodity_surcharge},queue='low')

    return {
      'id': str(commodity_surcharge.id)
    }