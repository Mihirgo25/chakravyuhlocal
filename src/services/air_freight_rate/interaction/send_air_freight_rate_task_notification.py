from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
from micro_services.client import partner
from configs.air_freight_rate_constants import ROLE_IDS_FOR_NOTIFICATIONS


def send_air_freight_rate_task_notification(task_id):
    task=AirFreightRateTasks.select().where(AirFreightRateTasks.id==task_id).first()

    send_communication(task.airline_id,task.airport_id)
    return {}

def send_communication(airline_id,airport_id,task_id):
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
            'service': 'air_freight_rate_task',
            'service_id': task_id,
            'template_name': 'air_freight_task_created',
            'service_objects': [{'service': 'location', 'id': airport_id }, { 'service': 'operator', 'id': airline_id }]
        }
        create_communication_background.apply_async(kwargs={'data':data},queue='communication')
