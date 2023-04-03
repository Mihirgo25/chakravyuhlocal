from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_commodity_surcharge import create_fcl_freight_rate_commodity_surcharge
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db

def create_audit(request):
    audit_data = {}
    audit_data['price'] = request['price']
    audit_data['currency'] = request['currency']
    audit_data['remarks'] = request.get('remarks')

    FclServiceAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = audit_data,
        object_id = request['id'],
        object_type='FclFreightRateCommoditySurcharge'
    )

def update_fcl_freight_rate_commodity_surcharge(request):
    object_type = 'Fcl_Freight_Rate_Commodity_Surcharge' 
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    fcl_freight_rate_commodity_surcharge = FclFreightRateCommoditySurcharge.get_by_id(request['id'])

    if not fcl_freight_rate_commodity_surcharge:
        raise HTTPException(status_code=404, detail="Commodity Surcharge not found")

    for k, v in request.items():
        if k in ['price', 'currency', 'remarks']:
            setattr(fcl_freight_rate_commodity_surcharge, k, v)

    if not fcl_freight_rate_commodity_surcharge.save():
        raise HTTPException(status_code=500, detail="Commodity Surcharge not updated")

    create_audit(request)

    return {'id':str(fcl_freight_rate_commodity_surcharge.id)}