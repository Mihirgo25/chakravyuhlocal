from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest 
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from celery_worker import create_communication_background
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import get_partner_users_by_expertise, get_partner_users
from micro_services.client import maps
from database.db_session import db
import uuid

def create_haulage_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    """
    Create haulage freight rate request
    Response Format:
        {"id": created_rate_request_id}
    """

    unique_object_params = {
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id'),
        'origin_location_id': request.get('origin_location_id'),
        'destination_location_id': request.get('destination_location_id'),
    }
    if request.get('preferred_shipping_line_ids'):
        request['preferred_shipping_line_ids'] = [uuid.UUID(str_id) for str_id in request['preferred_shipping_line_ids']]

    request_object = HaulageFreightRateRequest.select().where(
        HaulageFreightRateRequest.source == request.get('source'),
        HaulageFreightRateRequest.source_id == request.get('source_id'),
        HaulageFreightRateRequest.performed_by_id == request.get('performed_by_id'),
        HaulageFreightRateRequest.performed_by_type == request.get('performed_by_type'),
        HaulageFreightRateRequest.performed_by_org_id == request.get('performed_by_org_id'),
        HaulageFreightRateRequest.origin_location_id == request.get('origin_location_id'),
        HaulageFreightRateRequest.destination_location_id == request.get('destination_location_id'),
        HaulageFreightRateRequest.transport_mode == request.get('transport_mode')
    ).first()

    if not request_object:
        request_object = HaulageFreightRateRequest(**unique_object_params)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(request_object, attr, value)
    request_object.save()

    create_audit(request,request_object.id)

    get_multiple_service_objects(request_object)

    send_notifications_to_supply_agents(request)

    return {
        'id': request_object.id
        }

def get_create_params(request):
    if request.get('cargo_readiness_date'):
        request['cargo_readiness_date'] = request.get('cargo_readiness_date')
    loc_ids = []

    if request.get('origin_location_id'):
        loc_ids.append(request.get('origin_location_id'))
    if request.get('destination_location_id'):
        loc_ids.append(request.get('destination_location_id'))
    
    obj = {'filters':{"id": loc_ids }, 'includes': {'id': True, 'name': True, 'type': True, 'is_icd': True, 'cluster_id': True, 'city_id': True, 'country_id':True, 'country_code': True, 'display_name': True, 'default_params_required': True}}
    locations = maps.list_locations(obj)['list']
    locations_hash = {}
    for loc in locations:
        locations_hash[loc['id']] = loc
    if request.get('origin_location_id'):
        request['origin_location'] = locations_hash[request.get('origin_location_id')]
    if request.get('destination_location_id'):
        request['destination_location'] = locations_hash[request.get('destination_location_id')]
        
    return {key:value for key,value in request.items() if key not in ['source', 'source_id', 'performed_by_id', 'performed_by_type', 'performed_by_org_id','origin_location_id', 'destination_location_id']} | ({'status': 'active'})

def create_audit(request, request_object_id):
    performed_by_id = request.get('performed_by_id')
    del request['performed_by_id']
    if request.get("transport_mode") == 'trailer':
        object_type="TrailerFreightRateRequest"
    else:
        object_type="HaulageFreightRateRequest"

    if request.get('preferred_shipping_line_ids'):
        request['preferred_shipping_line_ids'] = [str(str_id) for str_id in request['preferred_shipping_line_ids']]
    
    HaulageFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_type = object_type,
        object_id = request_object_id
    )

def supply_agents_to_notify(request):

    locations_data = HaulageFreightRateRequest.select(HaulageFreightRateRequest.origin_location_id, HaulageFreightRateRequest.origin_country_id, HaulageFreightRateRequest.destination_location_id, HaulageFreightRateRequest.destination_country_id).where(HaulageFreightRateRequest.source_id == request['source_id']).limit(1).dicts().get()
    origin_locations = list(filter(None,[str(value or "") for key,value in locations_data.items() if key in ['origin_location_id', 'origin_country_id']]))
    destination_locations =   list(filter(None,[str(value or "") for key,value in locations_data.items() if key in ['destination_location_id', 'destination_country_id']]))

    supply_agents_data = get_partner_users_by_expertise('haulage_freight', origin_locations, destination_locations)
    supply_agents_list = list(set([item['partner_user_id'] for item in supply_agents_data]))

    supply_agents_user_data = get_partner_users(supply_agents_list)
    if supply_agents_user_data:
        supply_agents_user_ids = list(set([str(data['user_id']) for data in  supply_agents_user_data]))
    else:
        supply_agents_user_ids=[]

    route_data = maps.list_locations({'filters': { 'id': [str(locations_data['origin_location_id']),str(locations_data['destination_location_id'])]}})['list']
    
    route = {key['id']:key['display_name'] for key in route_data}

    return { 'user_ids': supply_agents_user_ids, 'origin_location': route[str(locations_data['origin_location_id'])], 'destination_location': route[str(locations_data['destination_location_id'])]}
    

def send_notifications_to_supply_agents(request):

    request_info = supply_agents_to_notify(request)
    if request_info['user_ids']:
        data = {
            'type': 'platform_notification',
            'service': 'spot_search',
            'service_id': request['source_id'],
            'template_name': 'missing_freight_rate_request_notification',
            'variables': { 'service_type': 'haulage freight',
                    'origin_location': request_info['origin_location'],
                    'destination_location': request_info['destination_location'] }
        }
    for user_id in request_info['user_ids']:
            data['user_id'] = user_id
            create_communication_background.apply_async(kwargs={'data':data},queue='communication')



