from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_seasonal_surcharge import create_fcl_freight_rate_seasonal_surcharge
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db

def create_audit(request, fcl_freight_rate_seasonal_surcharge_id):
    audit_data = {}
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()
    audit_data['price'] = request['price']
    audit_data['currency'] = request['currency']
    audit_data['remarks'] = request.get('remarks')

    FclServiceAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = audit_data,
        object_id = fcl_freight_rate_seasonal_surcharge_id,
        object_type = 'FclFreightRateSeasonalSurcharge'
    )

def update_fcl_freight_rate_seasonal_surcharge(request):
    object_type = 'Fcl_Freight_Rate_Seasonal_Surcharge' 
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    fcl_freight_rate_seasonal_surcharge = FclFreightRateSeasonalSurcharge.get(id=request['id'])

    if not fcl_freight_rate_seasonal_surcharge:
        raise HTTPException(status_code=400, detail="Seasonal Surcharge not found")
    
    for k, v in request.items():
        if k in ['price', 'currency', 'validity_start', 'validity_end', 'remarks']:
            setattr(fcl_freight_rate_seasonal_surcharge, k, v)

    if not fcl_freight_rate_seasonal_surcharge.save():
        raise HTTPException(status_code=500, detail="Seasonal Surcharge not updated")

    create_audit(request, fcl_freight_rate_seasonal_surcharge.id)