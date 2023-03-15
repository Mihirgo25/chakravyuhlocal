from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import json
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from configs.global_constants import HAZ_CLASSES
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import to_dict
from rails_client import client
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize
from database.db_session import db

def create_audit(request, freight_id):

    performed_by_id = request['performed_by_id']
    del request['performed_by_id']
    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request
    )

def execute_transaction(request):
    with db.atomic() as transaction:
        try:
            return create_fcl_freight_rate_task(request)
        except Exception as e:
            transaction.rollback()
            print(e)
            return e
            raise HTTPException(status_code=500,detail='Creation Failed')


def create_fcl_freight_rate_task(request):
    request = to_dict(request)
    object_unique_params = {
        'service': request.get("service"),
        'port_id': request.get("port_id"),
        'main_port_id': request.get("main_port_id"),
        'container_size': request.get("container_size"),
        'container_type': request.get("container_type"),
        'commodity': request.get("commodity") if request["commodity"] in HAZ_CLASSES else None,
        'trade_type': request.get("trade_type"),
        'shipping_line_id': request.get("shipping_line_id"),
        'source': request.get("source"),
        'task_type': request.get('task_type'),
        'status': 'pending'
    }

    task = find_or_initialize(FclFreightRateTask,**row)

    if request.get('shipment_id') is not None:
        try:
            sid = client.ruby.get_shipment(request['shipment_id'])['summary']['serial_id']
        except:
            sid = None
        task.shipment_serial_ids.append(sid)
    if task.source_count:
        task.source_count = int(task.source_count) + 1
    else:
        task.source_count=1
    if request.get('rate') is not None:
        task.job_data = {"rate": request['rate']}

    task.status = 'pending'

    if not task.validate():
        raise HTTPException(status_code=500, detail="Unable to create task")
    else:
        task.save()
    
    create_audit(request, task.id)

    # SendFclFreightRateTaskNotification.delay_until(5.seconds.from_now, queue: 'low').run!({ task_id: task.id })

    return {
      "id": task.id
    }

# def find_or_initialize(**kwargs):
#   try:
#     obj = FclFreightRateTask.get(**kwargs)
#   except FclFreightRateTask.DoesNotExist:
#     obj = FclFreightRateTask(**kwargs)
#   return obj