from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from database.db_session import db
from micro_services.client import *
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from celery_worker import create_communication_background, update_multiple_service_objects


def create_fcl_freight_rate_request(request):
    with db.atomic() as transaction:
        try:
            data = execute_transaction_code(request)
            return data
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    if type(request) != dict:
        request = request.__dict__

    unique_object_params = {
        'source': request['source'],
        'source_id': request['source_id'],
        'performed_by_id': request['performed_by_id'],
        'performed_by_type': request['performed_by_type'],
        'performed_by_org_id': request['performed_by_org_id']
    }

    request_object = FclFreightRateRequest.select().where(
        FclFreightRateRequest.source == request['source'],
        FclFreightRateRequest.source_id == request['source_id'],
        FclFreightRateRequest.performed_by_id == request['performed_by_id'],
        FclFreightRateRequest.performed_by_type == request['performed_by_type'],
        FclFreightRateRequest.performed_by_org_id == request['performed_by_org_id']
    ).first()

    if not request_object:
        request_object = FclFreightRateRequest(**unique_object_params)

    create_params = get_create_params(request)

    for attr, value in create_params.items():
        setattr(request_object, attr, value)

    request_object.set_location()

    if request_object.validate():
        request_object.save()

        create_audit(request, request_object.id)

        update_multiple_service_objects.apply_async(kwargs={'object':request_object},queue='low')

        send_notifications_to_supply_agents(request)

        return {
        'id': request_object.id
        }

def get_create_params(request):
    return {key:value for key,value in request.items() if key not in ['source', 'source_id', 'performed_by_id', 'performed_by_type', 'performed_by_org_id']} | ({'status': 'active' })

def supply_agents_to_notify(request):

    locations_data = FclFreightRateRequest.select(FclFreightRateRequest.origin_port_id, FclFreightRateRequest.origin_country_id, FclFreightRateRequest.origin_continent_id, FclFreightRateRequest.origin_trade_id, FclFreightRateRequest.destination_port_id, FclFreightRateRequest.destination_country_id, FclFreightRateRequest.destination_continent_id, FclFreightRateRequest.destination_trade_id).where(FclFreightRateRequest.source_id == request['source_id']).limit(1).dicts().get()
    origin_locations = list(filter(None,[str(value) for key,value in locations_data.items() if key in ['origin_port_id', 'origin_country_id', 'origin_continent_id', 'origin_trade_id']]))
    destination_locations =   list(filter(None,[str(value) for key,value in locations_data.items() if key in ['destination_port_id', 'destination_country_id', 'destination_continent_id', 'destination_trade_id']]))

    supply_agents_data= organization.list_partner_user_expertises({ 'filters': { 'service_type': 'fcl_freight', 'status': 'active', 'origin_location_id': origin_locations, 'destination_location_id':destination_locations }, 'pagination_data_required': False, 'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT })['list']
    supply_agents_list = list(set([item['partner_user_id'] for item in supply_agents_data]))

    supply_agents_user_data = organization.list_partner_users({ 'filters': { 'id': supply_agents_list }, 'pagination_data_required': False, 'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT })['list']
    supply_agents_user_ids = list(set([str(data['user_id']) for data in  supply_agents_user_data]))
    try:
        route_data = maps.list_locations({'filters': { 'id': [str(locations_data['origin_port_id']),str(locations_data['destination_port_id'])]}})['list']
    except Exception as e:
        print(e)

    route = {key['id']:key['display_name'] for key in route_data}
    try:
        return { 'user_ids': supply_agents_user_ids, 'origin_location': route[str(locations_data['origin_port_id'])], 'destination_location': route[str(locations_data['destination_port_id'])]}
    except Exception as e:
        print(e)


def send_notifications_to_supply_agents(request):

    request_info = supply_agents_to_notify(request)
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
        # create_communication_background.apply_async(args=data,queue='communication')



def create_audit(request, request_object_id):
    performed_by_id = request['performed_by_id']
    del request['performed_by_id']
    request['cargo_readiness_date'] = request['cargo_readiness_date'].isoformat()

    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_type = 'FclFreightRateRequest',
        object_id = request_object_id
    )
