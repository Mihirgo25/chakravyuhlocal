from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi import HTTPException
from database.db_session import db



def create_audit(request,air_freight_local_id):
    audit_data={}
    audit_data['data'] = request.get('data')
    audit_data['selected_suggested_rate_id'] = request.get('selected_suggested_rate_id')

    AirServiceAudit.create(

    )

def create_air_freight_rate_local(request):
    object_type='Air_Freight_Rate_Local'
    query=""
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    row={
        'airport_id':request.get('airport_id'),
        'airline_id':request.get('airline_id'),
        'trade_type':request.get('trade_type'),
        'commodity':request.get('commodity'),
        'service_provider_id':request.get('service_provider_id')
    }

    air_freight_local=AirFreightRateLocal.select().where(
        AirFreightRateLocal.airport_id == request.get('airport_id'),
        AirFreightRateLocal.airline_id ==request.get('airline_id'),
        AirFreightRateLocal.trade_type == request.get('trade_type'),
        AirFreightRateLocal.commodity== request.get('commodity'),
        AirFreightRateLocal.service_provider_id==request.get('service_provider_id')).first()
    
    if not air_freight_local:
        air_freight_local=AirFreightRateLocal(**row)

