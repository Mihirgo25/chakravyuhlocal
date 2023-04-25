from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from configs.global_constants import HAZ_CLASSES
from micro_services.client import *
from database.db_session import db

def create_audit(request, task_id):
    performed_by_id = request['performed_by_id']
    del request['performed_by_id']

    FclServiceAudit.create(
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_id = task_id,
        object_type = 'FclFreightRateTask'
    )

def create_fcl_freight_rate_task(request):
    object_type = 'Fcl_Freight_Rate_Task'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    from celery_worker import update_multiple_service_objects
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

    commodity = None
    if 'commodity' in request and request["commodity"] in HAZ_CLASSES:
        commodity = request["commodity"]


    task = FclFreightRateTask.select().where(
        FclFreightRateTask.service == request.get("service"),
        FclFreightRateTask.port_id == request.get("port_id"),
        FclFreightRateTask.main_port_id == request.get("main_port_id"),
        FclFreightRateTask.container_size == request.get("container_size"),
        FclFreightRateTask.container_type == request.get("container_type"),
        FclFreightRateTask.commodity == commodity,
        FclFreightRateTask.trade_type == request.get("trade_type"),
        FclFreightRateTask.shipping_line_id == request.get("shipping_line_id"),
        FclFreightRateTask.source == request.get("source"),
        FclFreightRateTask.task_type == request.get('task_type'),
        FclFreightRateTask.status == 'pending').first()

    if not task:
        task = FclFreightRateTask(**object_unique_params)
        task.shipment_serial_ids=[]

    if request.get('shipment_id') is not None:
        try:
            sid = shipment.get_shipment({'id':request['shipment_id']})['summary']['serial_id']
            task.shipment_serial_ids.append(sid)
        except:
            sid = None

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
    update_multiple_service_objects.apply_async(kwargs={'object':task},queue='low')
    # send_fcl_freight_rate_task_notifications.apply_async(kwargs={'task_id':task.id},queue='low')

    return {
      "id": task.id
    }
