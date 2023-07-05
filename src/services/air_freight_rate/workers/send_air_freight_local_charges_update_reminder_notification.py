from database.rails_db import get_supply_agents
from micro_services.client import common


def execute():
    supply_agents=get_supply_agents()
    if not supply_agents:
        return  
    
    for supply_agent in supply_agents:
        send_notification_to_update_local_charges(supply_agent)

def send_notification_to_update_local_charges(supply_agent):
    notification_data = {
      'type': 'platform_notification',
      'user_id': supply_agent['user_id'],
      'service': 'partner_user',
      'service_id': supply_agent['user_id'],
      'template_name': 'reminder_air_freight_local_charges'
    }
    common.create_communication(notification_data)