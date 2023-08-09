from fastapi import HTTPException
from database.db_session import db
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from services.ftl_freight_rate.models.ftl_freight_rate_request import (
    FtlFreightRateRequest,
)
from micro_services.client import maps
from celery_worker import create_communication_background,update_multiple_service_objects
from database.rails_db import get_partner_users_by_expertise, get_partner_users
from datetime import datetime, timedelta
from configs.fcl_freight_rate_constants import EXPECTED_TAT_RATE_FEEDBACK_REVERT, RATE_FEEDBACK_RELEVANT_ROLE_ID
from services.ftl_freight_rate.helpers.ftl_freight_rate_helpers import convert_date_format



def create_ftl_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    unique_object_params = {
        "source": request.get("source"),
        "source_id": request.get("source_id"),
        "performed_by_id": request.get("performed_by_id"),
        "performed_by_type": request.get("performed_by_type"),
        "performed_by_org_id": request.get("performed_by_org_id"),
    }
    request_object = (
        FtlFreightRateRequest.select()
        .where(
            FtlFreightRateRequest.source == request.get("source"),
            FtlFreightRateRequest.source_id == request.get("source_id"),
            FtlFreightRateRequest.performed_by_id == request.get("performed_by_id"),
            FtlFreightRateRequest.performed_by_type == request.get("performed_by_type"),
            FtlFreightRateRequest.performed_by_org_id
            == request.get("performed_by_org_id"),
        )
        .first()
    )
    if not request_object:
        request_object = FtlFreightRateRequest(**unique_object_params)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        if value:
            setattr(request_object, attr, value)

    request_object.set_location()
    request_object.save()

    send_notification_to_relevant_supply_agents(request)

    create_audit(request, request_object.id)

    update_multiple_service_objects.apply_async(kwargs={'object':request_object},queue='low')

    return {
        'id': str(request_object.id)
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


def send_notification_to_relevant_supply_agents(request):
    locations_data = FtlFreightRateRequest.select(FtlFreightRateRequest.origin_location_id, FtlFreightRateRequest.origin_country_id, FtlFreightRateRequest.origin_city_id, FtlFreightRateRequest.destination_location_id, FtlFreightRateRequest.destination_country_id, FtlFreightRateRequest.destination_city_id).where(FtlFreightRateRequest.source_id == request['source_id']).limit(1).dicts().get()
    origin_locations = list(filter(None,[str(value or "") for key,value in locations_data.items() if key in ['origin_location_id', 'origin_country_id', 'origin_city_id']]))
    destination_locations =   list(filter(None,[str(value or "") for key,value in locations_data.items() if key in ['destination_location_id', 'destination_country_id', 'destination_city_id']]))

    supply_agents_user_ids = get_relevant_supply_agents('ftl_freight', origin_locations, destination_locations)

    try:
        route_data = maps.list_locations({'filters': { 'id': [str(locations_data['origin_location_id']),str(locations_data['destination_location_id'])]}})['list']
    except Exception as error_message:
        raise HTTPException(status_code=400, detail=error_message)


    route = {key['id']:key['display_name'] for key in route_data}
    try:
        request_info = { 'user_ids': supply_agents_user_ids, 'origin_location': route[str(locations_data['origin_location_id'])], 'destination_location': route[str(locations_data['destination_location_id'])]}
        send_notifications_to_supply_agents(request, request_info)
    except Exception as error_message:
        raise HTTPException(status_code=400, detail=error_message)



def send_notifications_to_supply_agents(request, request_info):

    if request_info['user_ids']:
        data = {
        'type': 'platform_notification',
        'service': 'spot_search',
        'service_id': request['source_id'],
        'template_name': 'missing_freight_rate_request_notification',
        'variables': { 'service_type': 'ftl freight',
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
        request['cargo_readiness_date'] = convert_date_format(request.get('cargo_readiness_date')).isoformat()

    FtlFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_type = 'FtlFreightRateRequest',
        object_id = request_object_id,
        sourced_by_id = request.get("sourced_by_id"),
        procured_by_id = request.get("procured_by_id")
    )
