from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db
from celery_worker import update_multiple_service_objects

def create_audit(request, seasonal_surcharge_id):

    audit_data = {}
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()
    audit_data['price'] = request['price']
    audit_data['currency'] = request['currency']
    audit_data['remarks'] = request.get('remarks')

    FclServiceAudit.create(
        rate_sheet_id = request.get('rate_sheet_id'),
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        sourced_by_id = request['sourced_by_id'],
        procured_by_id = request['procured_by_id'],
        data = audit_data,
        object_id = seasonal_surcharge_id,
        object_type = 'FclFreightRateSeasonalSurcharge'
    )

def create_fcl_freight_rate_seasonal_surcharge(request):
    object_type = 'Fcl_Freight_Rate_Seasonal_Surcharge' 
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
        'origin_location_id' : request["origin_location_id"],
        'destination_location_id' : request["destination_location_id"],
        'container_size' : request["container_size"],
        'container_type' : request["container_type"],
        'shipping_line_id' : request["shipping_line_id"],
        'service_provider_id' : request["service_provider_id"],
        'code' : request["code"]
        }

    seasonal_surcharge = FclFreightRateSeasonalSurcharge.select().where(
        FclFreightRateSeasonalSurcharge.origin_location_id == request["origin_location_id"],
        FclFreightRateSeasonalSurcharge.destination_location_id == request["destination_location_id"],
        FclFreightRateSeasonalSurcharge.container_size == request["container_size"],
        FclFreightRateSeasonalSurcharge.container_type == request["container_type"],
        FclFreightRateSeasonalSurcharge.shipping_line_id == request["shipping_line_id"],
        FclFreightRateSeasonalSurcharge.service_provider_id == request["service_provider_id"],
        FclFreightRateSeasonalSurcharge.code == request["code"]).first()

    if not seasonal_surcharge:
        seasonal_surcharge = FclFreightRateSeasonalSurcharge(**row)

    for k, v in request.items():
        if k in ['price', 'currency', 'validity_start', 'validity_end', 'remarks']:
            setattr(seasonal_surcharge, k, v)
    seasonal_surcharge.validate()

    seasonal_surcharge.sourced_by_id = request['sourced_by_id']
    seasonal_surcharge.procured_by_id = request['procured_by_id']

    if not seasonal_surcharge.save():
        raise HTTPException(status_code=422, detail="Seasonal Surcharge not saved")
    
    seasonal_surcharge.update_freight_objects()

    create_audit(request, seasonal_surcharge.id)
    update_multiple_service_objects.apply_async(kwargs={'object':seasonal_surcharge},queue='low')


    return {
      'id': str(seasonal_surcharge.id)
    }
