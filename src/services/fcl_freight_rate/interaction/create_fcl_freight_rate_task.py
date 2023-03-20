from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from configs.global_constants import HAZ_CLASSES
from rails_client import client
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
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e


def execute_transaction_code(request):
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

    task = FclFreightRateTask.select().where(
        FclFreightRateTask.service == request.get("service"),
        FclFreightRateTask.port_id == request.get("port_id"),
        FclFreightRateTask.main_port_id == request.get("main_port_id"),
        FclFreightRateTask.container_size == request.get("container_size"),
        FclFreightRateTask.container_type == request.get("container_type"),
        FclFreightRateTask.commodity == request.get("commodity") if request["commodity"] in HAZ_CLASSES else FclFreightRateTask.commodity.is_null(True),
        FclFreightRateTask.trade_type == request.get("trade_type"),
        FclFreightRateTask.shipping_line_id == request.get("shipping_line_id"),
        FclFreightRateTask.source == request.get("source"),
        FclFreightRateTask.task_type == request.get('task_type'),
        FclFreightRateTask.status == 'pending').first()

    if not task:
        task = FclFreightRateTask(**object_unique_params)

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
