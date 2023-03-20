from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from celery_worker import celery
from services.fcl_freight_rate.models.partner_user import PartnerUser
from configs.fcl_freight_rate_constants import *

def send_fcl_freight_rate_task_notification(task_id):
    task = FclFreightRateTask.select().where(FclFreightRateTask.id == task_id).dicts().get()

    send_communication(task['shipping_line_id'], task['port_id'], task_id)

    return {}
  

def send_communication(shipping_line_id, port_id,task_id):
    partners_list = PartnerUser.select(PartnerUser.user_id).where(PartnerUser.role_ids.in_(','.join(ROLE_IDS_FOR_NOTIFICATIONS)), PartnerUser.status == 'active')

    for partner_user in partners_list:
        data = {
            'type': 'platform_notification',
            'user_id': partner_user['user_id'],
            'service': 'fcl_freight_rate_task',
            'service_id': task_id,
            'template_name': 'fcl_freight_task_created',
            'service_objects': [{'service': 'location', 'id': port_id }, { 'service': 'operator', 'id': shipping_line_id }]
        }

    # client.ruby.CreateCommunication.delay(queue: 'communication', retry: 0).run!(data)

    # app = Celery('tasks', broker='amqp://guest@localhost//')

    # @app.task(queue='communication', retry=False)
    # def run(data):
    #     client.ruby.create_communication(data)
    #     pass

    # run.delay(data)

