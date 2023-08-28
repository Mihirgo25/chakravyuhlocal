from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from database.db_session import db
from micro_services.client import *
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from celery_worker import create_communication_background, update_multiple_service_objects, update_fcl_freight_rate_request_in_delay
from database.rails_db import get_partner_users_by_expertise, get_partner_users
from datetime import datetime, timedelta
from configs.fcl_freight_rate_constants import EXPECTED_TAT_RATE_FEEDBACK_REVERT, RATE_FEEDBACK_RELEVANT_ROLE_ID
# from services.bramhastra.celery import send_request_stats_in_delay


def create_fcl_freight_rate_request(request):
    object_type = 'Fcl_Freight_Rate_Request' 
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    action = 'update'
    
    unique_object_params = {
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    request_object = FclFreightRateRequest.select().where(
        FclFreightRateRequest.source == request.get('source'),
        FclFreightRateRequest.source_id == request.get('source_id'),
        FclFreightRateRequest.performed_by_id == request.get('performed_by_id'),
        FclFreightRateRequest.performed_by_type == request.get('performed_by_type'),
        FclFreightRateRequest.performed_by_org_id == request.get('performed_by_org_id')
    ).first()

    if not request_object:
        request_object = FclFreightRateRequest(**unique_object_params)
        action = 'create'

    create_params = get_create_params(request)

    for attr, value in create_params.items():
        setattr(request_object, attr, value)

    request_object.set_location()

    if request_object.validate():
        request_object.save()

        set_relevant_supply_agents(request, request_object.id)

        create_audit(request, request_object.id)

        update_multiple_service_objects.apply_async(kwargs={'object':request_object},queue='low')
         
        # send_request_stats_in_delay.apply_async(kwargs = {'action':action,'object':request_object},queue = 'statistics')

        return {
        'id': request_object.id
        }

def get_create_params(request):
    expiration_time = datetime.now() + timedelta(seconds = EXPECTED_TAT_RATE_FEEDBACK_REVERT * 60 * 60)
    return {key:value for key,value in request.items() if key not in ['source', 'source_id', 'performed_by_id', 'performed_by_type', 'performed_by_org_id']} | ({'status': 'active' , 'expiration_time': expiration_time})

def get_relevant_supply_agents(service, origin_locations, destination_locations):
    supply_agents_data = get_partner_users_by_expertise(service, origin_locations, destination_locations)
    supply_agents_list = list(set([item['partner_user_id'] for item in supply_agents_data]))

    supply_agents_user_data = get_partner_users(supply_agents_list, role_ids= list(RATE_FEEDBACK_RELEVANT_ROLE_ID.values()))
    if supply_agents_user_data:
        supply_agents_user_ids = list(set([str(data['user_id']) for data in  supply_agents_user_data]))
    else:
        supply_agents_user_ids=[]
    return supply_agents_user_ids


def set_relevant_supply_agents(request, fcl_freight_rate_request_id):
    locations_data = FclFreightRateRequest.select(FclFreightRateRequest.origin_port_id, FclFreightRateRequest.origin_country_id, FclFreightRateRequest.origin_continent_id, FclFreightRateRequest.origin_trade_id, FclFreightRateRequest.destination_port_id, FclFreightRateRequest.destination_country_id, FclFreightRateRequest.destination_continent_id, FclFreightRateRequest.destination_trade_id).where(FclFreightRateRequest.source_id == request['source_id']).limit(1).dicts().get()
    origin_locations = list(filter(None,[str(value or "") for key,value in locations_data.items() if key in ['origin_port_id', 'origin_country_id', 'origin_continent_id', 'origin_trade_id']]))
    destination_locations =   list(filter(None,[str(value or "") for key,value in locations_data.items() if key in ['destination_port_id', 'destination_country_id', 'destination_continent_id', 'destination_trade_id']]))

    supply_agents_user_ids = get_relevant_supply_agents('fcl_freight', origin_locations, destination_locations)

    update_fcl_freight_rate_request_in_delay({'fcl_freight_rate_request_id': fcl_freight_rate_request_id, 'relevant_supply_agent_ids': supply_agents_user_ids, 'performed_by_id': request.get('performed_by_id'),'ignore': True})
        
    try:
        route_data = maps.list_locations({'filters': { 'id': [str(locations_data['origin_port_id']),str(locations_data['destination_port_id'])]}})['list']
    except Exception as e:
        print(e)

    route = {key['id']:key['display_name'] for key in route_data}
    try:
        request_info = { 'user_ids': supply_agents_user_ids, 'origin_location': route[str(locations_data['origin_port_id'])], 'destination_location': route[str(locations_data['destination_port_id'])]}
        send_notifications_to_supply_agents(request, request_info)
    except Exception as e:
        print(e)



def send_notifications_to_supply_agents(request, request_info):

    if request_info['user_ids']:
        data = {
        'type': 'platform_notification',
        'service': 'spot_search',
        'service_id': request['source_id'],
        'template_name': 'missing_freight_rate_request_notification',
        'variables': { 'service_type': 'fcl freight',
                    'origin_location': request_info['origin_location'],
                    'destination_location': request_info['destination_location'] }
        }
        for user_id in request_info['user_ids']:
            data['user_id'] = user_id
            create_communication_background.apply_async(kwargs={'data':data},queue='communication')



def create_audit(request, request_object_id):
    performed_by_id = request.get('performed_by_id')
    del request['performed_by_id']
    if request.get('cargo_readiness_date'):
        request['cargo_readiness_date'] = request.get('cargo_readiness_date').isoformat()

    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_type = 'FclFreightRateRequest',
        object_id = request_object_id
    )

