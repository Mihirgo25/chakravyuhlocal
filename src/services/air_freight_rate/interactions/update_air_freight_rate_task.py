from datetime import datetime
from database.db_session import db
from fastapi import HTTPException
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
from services.air_freight_rate.constants.air_freight_rate_constants import * 
from services.air_freight_rate.interactions.create_air_freight_rate_local import create_air_freight_rate_local
from micro_services.client import *

def create_audit(request):
    data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id','id'] and not value == None}

    AirServiceAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = data,
        object_id = request['id'],
        object_type = 'AirFreightRateTask'
    )


def update_air_freight_rate_task(request):
    if not validate_closing_remarks(request):
        raise HTTPException(status_code=400,detail=f"{request['closing_remarks']} is invalid")
    
    with db.atomic():
        return execute_transaction_code(request)
    
def validate_closing_remarks(request):
    if request.get('closing_remarks') and  request.get('closing_remarks') not in TECHOPS_TASK_ABORT_REASONS:
        return False
    return True

def execute_transaction_code(request):
    request['service_provider_id']=DEFAULT_SERVICE_PROVIDER_ID
    request['sourced_by_id']=DEFAULT_SOURCED_BY_ID
    request['procured_by_id']=DEFAULT_PROCURED_BY_ID

    task=AirFreightRateTasks.select().where(AirFreightRateTasks.id==request.get('id')).first()


    if not task:
        raise HTTPException(status_code=404,detail="Task Is Not Found")
    
    update_params=get_update_params(request)
   
    for attr, value in update_params.items():
        setattr(task, attr, value)

    try :
        task.save()
    except :
        raise HTTPException(status_code = 500, detail = 'Error in update params')
    
    create_audit(request)
    
    if request['status']:
        return {'id': str(task.id)}
    
    result=create_air_freight_local_rate(task,request)

    update_shipment_local_charges(task,request)

    get_multiple_service_objects(task)
def create_air_freight_local_rate(task,request):
    rate=task.completion_data['rate']

    create_params={
      'performed_by_id': request.get('performed_by_id'),
      'service_provider_id': request['service_provider_id'],
      'procured_by_id': request['procured_by_id'],
      'sourced_by_id': request['sourced_by_id'],
     'source': 'tech_ops_dashboard', #todo we dont't store source for air local (should be added to audit?)
      'trade_type': task.trade_type,
      'airport_id': task.airport_id,
      'commodity': task.commodity,
      'commodity_type': task.commodity_type,
      'airline_id': task.airline_id,
      'line_items': rate['line_items']
    }
    try:
        id = create_air_freight_rate_local(create_params)
    except Exception as e:
        raise HTTPException(status_code = 400, detail = 'Error while creating Local')

def update_shipment_local_charges(task,request):
    rate=task.completion_data['rate']
    try:
        result= shipment.bulk_update_shipment_quotations({
            'performed_by_id': request['performed_by_id'],
            'performed_by_type': request['performed_by_type'],
            'service': 'air_freight_local',
            'line_items': rate['line_items'],
            'filters': {
            'airport_id': task.airport_id,
            'commodity': task.commodity,
            'trade_type': task.trade_type,
            'airline_id': task.airline_id,
            'service_provider_id': request['service_provider_id']
            }
        })
        return result
    except:
        return {}
    
def get_update_params(request):

    update_params={
        'completion_data':{
            'sourced_by_id':request['sourced_by_id'],
            'procured_by_id':request['procured_by_id'],
            'service_provider_id':request['service_provider_id'],
            'rate':request.get('rate')
        }
    }
    if request.get('status'):
        update_params={'completion_data':{ 'closing_remarks':request['closing_remarks']}}
    update_params['completed_by_id'] = request['performed_by_id']
    update_params['completed_at'] = datetime.now()
    if request.get('status'):
        update_params['status'] = request['status']
    else:
        update_params['status'] = 'completed'
    return update_params