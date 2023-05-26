from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from services.air_freight_rate.interaction.create_air_freight_rate_surcharge import create_air_freight_rate_surcharge
from fastapi import FastAPI, HTTPException
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from database.db_session import db

def create_audit(request):
    AirServiceAudit.create(
        action_name = 'update',
        performed_by_id = request.get('performed_by_id'),
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id= request.get('procured_by_id'),
        data = get_update_params(request),
        object_id = request['id'],
        object_type='AirFreightRateSurcharge'
    )
def get_update_params(request):
    interaction_inputs = {key: value for key, value in request.items() if key not in ['performed_by_id', 'id', 'procured_by_id', 'sourced_by_id']}
    return interaction_inputs

def update_air_freight_rate_surcharge(request):
    object_type = 'Air_Freight_Rate_Surcharge' 
    query = "create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    air_freight_rate_surcharge = AirFreightRateSurcharge.get_by_id(request['id'])
    if not air_freight_rate_surcharge:
        raise HTTPException(status_code=400, detail=" Surcharge not found")










