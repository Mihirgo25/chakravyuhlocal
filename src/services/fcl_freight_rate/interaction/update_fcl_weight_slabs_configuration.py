from database.db_session import db
from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
from datetime import datetime
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit

def create_audit(request):

    data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id','id'] and not value == None}

    FclServiceAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = data,
        object_id = request['id'],
        object_type = 'FclWeightSlabsConfiguration'
    )

def update_fcl_weight_slabs_configuration(request):
    object_type = 'Fcl_Weight_Slabs_Configuration'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):

    
    updated_configuration = FclWeightSlabsConfiguration.get(**{'id' : request['id']})
    
    if not updated_configuration:
        raise HTTPException(status_code=400,detail='Weight Slab Not Found')
    request['updated_at'] = datetime.now()
    request['price'] = request.get('slabs')[0].get('price')
    request['currency'] = request.get('slabs')[0].get('currency')
    
    for attr,value in request.items():
        setattr(updated_configuration, attr, value)

    if not updated_configuration.save():
        raise HTTPException(status_code=500, detail="Commodity Cluster not saved")

    create_audit(request)
    return {
    'id': request['id']
    }