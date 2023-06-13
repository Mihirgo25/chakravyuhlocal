from services.fcl_customs_rate.models.fcl_customs_rate_request import FclCustomsRateRequest
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from database.db_session import db
from database.rails_db import get_partner_users_by_expertise, get_partner_users
from micro_services.client import maps
from celery_worker import create_communication_background, update_multiple_service_objects
from fastapi import HTTPException

def create_fcl_customs_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    search_params = {
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    customs_request = FclCustomsRateRequest.select().where(
        FclCustomsRateRequest.source == request.get('source'),
        FclCustomsRateRequest.source_id == request.get('source_id'),
        FclCustomsRateRequest.performed_by_id == request.get('performed_by_id'),
        FclCustomsRateRequest.performed_by_type == request.get('performed_by_type'),
        FclCustomsRateRequest.performed_by_org_id == request.get('performed_by_org_id')).first()

    if not customs_request:
        customs_request = FclCustomsRateRequest(**search_params)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(customs_request, attr, value)

    customs_request.set_port()
    customs_request.validate_source_id()
    
    try:
        customs_request.save()
    except:
        raise HTTPException(status_code=500, detail='Request did not save')

    create_audit(request, customs_request.id)
    update_multiple_service_objects.apply_async(kwargs={'object':customs_request},queue='low')
    send_notifications_to_supply_agents(request)
    
    return {
      'id': customs_request.id
    }


def supply_agents_to_notify(request):
    locations_data = FclCustomsRateRequest.select(FclCustomsRateRequest.port_id, FclCustomsRateRequest.country_id).where(FclCustomsRateRequest.source_id == request.get('source_id')).dicts().get()
    locations = list(filter(None,[str(value or "") for key,value in locations_data.items()]))

    supply_agents_data = get_partner_users_by_expertise('fcl_customs', locations )
    supply_agents_list = list(set([item.get('partner_user_id') for item in supply_agents_data]))

    supply_agents_user_data = get_partner_users(supply_agents_list)
    supply_agents_user_ids = list(set([str(data['user_id']) for data in  supply_agents_user_data])) if supply_agents_user_data else None

    port_ids = locations_data.get('port_id')
    try:
        route_data = maps.list_locations({'filters':{'id':port_ids}})['list']
    except Exception as e:
        print(e)

    route = {key['id']:key['display_name'] for key in route_data}
    return { 'user_ids': supply_agents_user_ids, 'location': route.get(str(locations_data.get('port_id') or '')) }

def send_notifications_to_supply_agents(request):
    request_info = supply_agents_to_notify(request)

    data = {
        'type': 'platform_notification',
        'service': 'spot_search',
        'service_id': request.get('source_id'),
        'template_name': 'missing_customs_rate_request_notification',
        'variables': { 
            'service_type': 'fcl customs',
            'location': request_info.get('location')
        }
    }

    for user_id in (request_info.get('user_ids') or []):
        data['user_id'] = user_id
        create_communication_background.apply_async(kwargs = {'data':data}, queue = 'communication')


def create_audit(request, customs_request_id):
    performed_by_id = request.get('performed_by_id')
    del request['performed_by_id']
    if request.get('cargo_readiness_date'):
        request['cargo_readiness_date'] = request.get('cargo_readiness_date').isoformat()
    
    FclCustomsRateAudit.create(
        object_id = customs_request_id,
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_type = 'FclCustomsRateRequest'
    )

def get_create_params(request):
    params = {
      'remarks': request.get('remarks'),
      'booking_params': request.get('booking_params'),
      'preferred_customs_rate': request.get('preferred_customs_rate'),
      'preferred_customs_rate_currency': request.get('preferred_customs_rate_currency'),
    #   'preferred_detention_free_days': request.get('preferred_detention_free_days'),
      'cargo_readiness_date': request.get('cargo_readiness_date'),
    #   'preferred_storage_free_days': request.get('preferred_storage_free_days'),
      'containers_count': request.get('containers_count'),
      'container_size': request.get('container_size'),
      'commodity': request.get('commodity'),
      'cargo_handling_type': request.get('cargo_handling_type'),
      'country_id': request.get('country_id'),
      'port_id': request.get('port_id'),
      'container_type': request.get('container_type'),
      'trade_type': request.get('trade_type'),
      'status': 'active'
    }

    return params