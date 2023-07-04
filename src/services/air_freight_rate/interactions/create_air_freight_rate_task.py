from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
from fastapi import HTTPException
from micro_services.client import *
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from celery_worker import update_multiple_service_objects,send_air_freight_rate_task_notification_in_delay


def create_audit(request,task_id):

    AirFreightRateAudit.create(
        action_name='create',
        data=request,
        performed_by_id=request.get('performed_by_id'),
        object_id=task_id,
        object_type='AirFreightRateTask'
    )

def execute(request):
    with db.atomic():
        return  create_air_freight_rate_task(request)
    
def create_air_freight_rate_task (request):
     
    row={
      'service': request.get('service'),
      'airport_id': request.get('airport_id'),
      'commodity': request.get('commodity'),
      'trade_type': request.get('trade_type'),
      'commodity_type': request.get('commodity_type'),
      'airline_id':request.get('airline_id'),
      'source':request.get('source'),
      'task_type':request.get('task_type'),
      'status': 'pending'
    }

    task=AirFreightRateTasks.select().where(
        AirFreightRateTasks.service==request.get('service'),
        AirFreightRateTasks.airport_id==request.get('airport_id'),
        AirFreightRateTasks.commodity==request.get('commodity'),
        AirFreightRateTasks.commodity_type==request.get('commodity_type'),
        AirFreightRateTasks.airline_id==request.get('airline_id'),
        AirFreightRateTasks.source==request.get('source'),
        AirFreightRateTasks.task_type==request.get('task_type'),
        AirFreightRateTasks.status== 'pending').first()
    
    if not task:
        task = AirFreightRateTasks(**row)
        task.shipment_serial_ids=[]
    
    if task.source_count:
        task.source_count=int(task.source_count)+1
    else:
        task.source_count=1

    if request.get('rate'):
        task.job_data={'rate':request.get('rate')}
    task.status='pending'

    if request.get('shipment_id'):
        try:
            sid = shipment.get_shipment({'id':request['shipment_id']})['summary']['serial_id']
            task.shipment_serial_ids.append(sid)
            task.shipment_serial_ids = list(set(task.shipment_serial_ids))
        except:
            raise HTTPException(status_code = 400, detail = "SID doesn't Exist")

    task.validate()
    try:
        task.save()
    except:
        raise HTTPException(status_code =500,detail='unable to create task')
    
    create_audit(request,task.id)

    update_multiple_service_objects.apply_async(kwargs={'object':task},queue='low')

    send_air_freight_rate_task_notification_in_delay.apply_async(kwargs={'task_id':task.id},queue='low')
    
    return{
        'id':task.id
    }
