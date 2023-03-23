from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from configs.fcl_freight_rate_constants import *
from micro_services.client import partner

def send_fcl_freight_rate_task_notification(task_id):
    task = FclFreightRateTask.select().where(FclFreightRateTask.id == task_id).dicts().get()

    send_communication(task['shipping_line_id'], task['port_id'], task_id)

    return {}

def send_communication(shipping_line_id, port_id,task_id):
    from celery_worker import create_communication_background
    partners_list = partner.list_partner_users({'filters':{'role_ids': ','.join(ROLE_IDS_FOR_NOTIFICATIONS), 'status' : 'active'}})
    if partners_list:
        partners_list = partners_list['list']
    else:
        partners_list = []

    for partner_user in partners_list:
        data = {
            'type': 'platform_notification',
            'user_id': partner_user['user_id'],
            'service': 'fcl_freight_rate_task',
            'service_id': task_id,
            'template_name': 'fcl_freight_task_created',
            'service_objects': [{'service': 'location', 'id': port_id }, { 'service': 'operator', 'id': shipping_line_id }]
        }
        create_communication_background.apply_async(args=data,queue='communication')

