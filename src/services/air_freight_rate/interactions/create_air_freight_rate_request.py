from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_request import (
    AirFreightRateRequest,
)
from datetime import *
from fastapi import HTTPException
from micro_services.client import *
from database.rails_db import get_partner_users_by_expertise, get_partner_users
from playhouse.postgres_ext import *
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from celery_worker import (
    update_multiple_service_objects,
    create_communication_background,
)


def create_air_freight_rate_request(request):
    object_type = "Air_Freight_Rate_Request"
    query = "create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(
        object_type.lower(), object_type.replace("_", "")
    )
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):

    existing_missing_request = AirFreightRateRequest.update(status="inactive").where(
        AirFreightRateRequest.source == "shipment",
        AirFreightRateRequest.source_id == request.get("source_id"),
        AirFreightRateRequest.status == "active",
    )

    unique_object_params = {
        "source": request.get("source"),
        "source_id": request.get("source_id"),
        "performed_by_id": request.get("performed_by_id"),
        "performed_by_type": request.get("performed_by_type"),
        "performed_by_org_id": request.get("performed_by_org_id"),
    }
    request_object = (
        AirFreightRateRequest.select()
        .where(
            AirFreightRateRequest.source == request.get("source"),
            AirFreightRateRequest.source_id == request.get("source_id"),
            AirFreightRateRequest.performed_by_id == request.get("performed_by_id"),
            AirFreightRateRequest.performed_by_type == request.get("performed_by_type"),
            AirFreightRateRequest.performed_by_org_id
            == request.get("performed_by_org_id"),
            AirFreightRateRequest.status == 'active'
        )
        .first()
    )

    if not request_object:
        request_object = AirFreightRateRequest(**unique_object_params)
    create_params = get_create_params(request)

    for attr, value in create_params.items():
        if attr =='preferred_airline_ids' and value:
            ids=[]
            for val in value:
                ids.append(uuid.UUID(str(val)))
            setattr(request_object,attr,ids)
        else:
            setattr(request_object, attr, value)
    
    request_object.set_locations()
    request_object.validate()
    try:
        request_object.save()
    except Exception as e:
        raise HTTPException(status_code = 400, detail = 'Request is Not Saved')

    create_audit(request, request_object.id)

    update_multiple_service_objects.apply_async(
        kwargs={"object": request_object}, queue="low"
    )

    if request_object.id:
        airports = get_locations(request_object)
        if airports:
            send_notification_for_rates_not_found(
                request, request_object, airports
            )
            send_notification_to_supply_agents(
                 request_object, airports
            )

    return {"id": str(request_object.id)}


def get_locations(request_object):
    location_ids = list(
        set(
            [
                str(request_object.origin_airport_id),
                str(request_object.destination_airport_id),
            ]
        )
    )
    locations = maps.list_locations({"filters": {"id": location_ids}})['list']
    for location in locations:
        if str(request_object.origin_airport_id) == str(location.get('id')):
            origin_location = location
        else:
            destination_location = location
    return [origin_location, destination_location]


def get_create_params(request):
    return {
        key: value
        for key, value in request.items()
        if key
        not in [
            "source",
            "source_id",
            "performed_by_id",
            "performed_by_type",
            "performed_by_org_id",
        ]
    } | ({"status": "active"})


def create_audit(request, request_object_id):
    performed_by_id = request.get("performed_by_id")
    del request["performed_by_id"]
    if request.get("cargo_readiness_date"):
        request["cargo_readiness_date"] = request.get(
            "cargo_readiness_date"
        ).isoformat()

    AirServiceAudit.create(
        action_name="create",
        performed_by_id=performed_by_id,
        data=request,
        object_type="AirFreightRateRequest",
        object_id=request_object_id,
    )


def send_notification_for_rates_not_found(request, request_object, airports):
    commodity = request_object.commodity
    if len(airports) < 2:
        return
    origin_airport = airports[0]
    destination_airport = airports[1]
    
    notification_data = {
        "type": "platform_notification",
        "user_id": request.get("performed_by_id"),
        "service": "spot_search",
        "service_id": str(request_object.source_id),
        "template_name": "air_freight_rates_not_found_on_any_sales_channel",
        "variables": {
            "origin_port": origin_airport.get('display_name'),
            "destination_port": destination_airport.get('display_name'),
            "commodity": commodity,
            "weight": request_object.weight,
        },
    }
    create_communication_background.apply_async(kwargs={"data": notification_data}, queue="communication")


def send_notification_to_supply_agents(request_object, airports):

    origin_location_ids = [str(t) for t in [request_object.origin_airport_id, request_object.origin_continent_id, request_object.origin_country_id] if t ]
    destination_location_ids = [str(t) for t in [request_object.destination_airport_id, request_object.destination_continent_id, request_object.destination_country_id] if t]

    supply_agents_data = get_partner_users_by_expertise("air_freight", origin_location_ids, destination_location_ids)

    supply_agents_list = list(set([item["partner_user_id"] for item in supply_agents_data]))

    supply_agents_user_data = get_partner_users(supply_agents_list)

    if supply_agents_user_data:
        supply_agents_user_ids = list(
            set([str(data["user_id"]) for data in supply_agents_user_data])
        )
    else:
        supply_agents_user_ids = []
    for supply_agents_user_id in supply_agents_user_ids:
        send_notification_for_new_search_made_for_rates(request_object, airports, supply_agents_user_id)


def send_notification_for_new_search_made_for_rates(request_object, airports, supply_agents_user_id):

    commodity = request_object.commodity
    if len(airports) < 2:
        return
    origin_airport = airports[0]
    destination_airport = airports[1]
    notification_data = {
        "type": "platform_notification",
        "user_id": supply_agents_user_id,
        "service": "spot_search",
        "service_id": str(request_object.source_id),
        "template_name": "air_freight_rates_not_available_for_new_search",
        "variables": {
            "origin_port": origin_airport,
            "destination_port": destination_airport,
            "commodity": commodity,
        },
    }
    create_communication_background.apply_async(kwargs={"data": notification_data}, queue="communication")
