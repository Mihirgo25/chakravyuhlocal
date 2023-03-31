from configs.fcl_freight_rate_constants import *
from database.db_session import db
from datetime import datetime
from micro_services.client import *
from configs.global_constants import HAZ_CLASSES
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from celery_worker import update_multiple_service_objects
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from fastapi import HTTPException

def create_audit(request):
    data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id','id'] and not value == None}

    FclServiceAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = data,
        object_id = request['id'],
        object_type = 'FclFreightRateTask'

    )
def update_fcl_freight_rate_task_data(request):
    if not validate_closing_remarks(request):
        return {request['closing_remarks'], 'is not valid'}
    
    with db.atomic() as transaction:
        object_type = 'Fcl_Freight_Rate_Task'
        query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
        db.execute_sql(query)
        try:
            data = execute_transaction_code(request)
            return data
        except Exception as e:
            transaction.rollback()
            return e

def validate_closing_remarks(request):
    if request['closing_remarks'] and request['closing_remarks'] not in TECHOPS_TASK_ABORT_REASONS:
        return False
    return True

def execute_transaction_code(request):
    request['service_provider_id'] = DEFAULT_SERVICE_PROVIDER_ID
    request['sourced_by_id'] = DEFAULT_SOURCED_BY_ID
    request['procured_by_id'] = DEFAULT_PROCURED_BY_ID

    task = FclFreightRateTask.select().where(FclFreightRateTask.id == request['id']).first()

    if not task:
        raise HTTPException(status_code = 422, detail = f"{request['id']} is invalid")
    
    update_params = get_update_params(request)
    for attr, value in update_params.items():
        setattr(task, attr, value)

    if not task.save():
        raise HTTPException(status_code = 500, detail = 'Error in update params')
    
    if request['status']:
        return {'id': str(task.id)}
    
    result = create_fcl_freight_local_rate(task,request) 
    
    update_shipment_local_charges(task,request)

    update_multiple_service_objects.apply_async(kwargs={'object':task},queue='low')

    create_audit(request)
    # if task['source'] == 'contract':
        # UpdateContractServiceTask.delay(queue: 'low').run!({ task_id: task.id, service_type: 'fcl_freight', rate: self.rate }) if task.source == 'contract'
 
    return {'id': str(task.id)}

def get_update_params(request):
    update_params = {
      'completion_data': {
        'sourced_by_id': request['sourced_by_id'],
        'procured_by_id': request['procured_by_id'],
        'service_provider_id': request['service_provider_id'],
        'rate': request['rate']
      }
    }
    if request['status']:
        update_params = { 'completion_data': { 'closing_remarks': request['closing_remarks'] } }

    update_params['completed_by_id'] = request['performed_by_id']
    update_params['completed_at'] = datetime.now()
    if request['status']:
        update_params['status'] = request['status']
    else:
        update_params['status'] = 'completed'

    return update_params

def create_fcl_freight_local_rate(task,request):
    rate = task.completion_data['rate']

    create_params = {
        'performed_by_id': request['performed_by_id'],
        'source': 'tech_ops_dashboard',
        'trade_type': task.trade_type,
        'port_id': task.port_id,
        'main_port_id': task.main_port_id,
        'container_size': task.container_size,
        'container_type': task.container_type,
        'commodity': task.commodity if task.commodity in HAZ_CLASSES else None,
        'shipping_line_id': task.shipping_line_id,
        'service_provider_id': request['service_provider_id'],
        'procured_by_id': request['procured_by_id'],
        'sourced_by_id': request['sourced_by_id'],
        'data': { 'line_items': rate['line_items'], 'detention': rate['detention'], 'demurrage': rate['demurrage'] }
      }

    return create_fcl_freight_rate_local(create_params)

def update_shipment_local_charges(task,request):
    rate = task.completion_data['rate']
    try:
        result = common.bulk_update_shipment_quotations({
        'performed_by_id': request['performed_by_id'],
        'performed_by_type': request['performed_by_type'],
        'service': 'fcl_freight_local',
        'line_items': rate['line_items'],
        'filters': {
            'port_id': task.port_id,
            'main_port_id': task.main_port_id,
            'container_size': task.container_size,
            'container_type': task.container_type,
            'commodity': task.commodity,
            'trade_type': task.trade_type,
            'shipping_line_id': task.shipping_line_id,
            'service_provider_id': request['service_provider_id']
        }
        })
        return result
    except:
        return {}