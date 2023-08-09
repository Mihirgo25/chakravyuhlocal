from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_request import (
    AirFreightRateRequest
)
from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from micro_services.client import *
from celery_worker import send_closed_notifications_to_sales_agent_function,send_closed_notifications_to_user_request
from fastapi.encoders import jsonable_encoder
from database.rails_db import (
    get_organization_partner,
)


def delete_air_freight_rate_request(request):
    object_type = "Air_Freight_Rate_Request"
    query = "create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(
        object_type.lower(), object_type.replace("_", "")
    )
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    request_objects = (
        AirFreightRateRequest.select(AirFreightRateRequest.id,AirFreightRateRequest.status,AirFreightRateRequest.closed_by_id,AirFreightRateRequest.closing_remarks,
        AirFreightRateRequest.source,AirFreightRateRequest.source_id,AirFreightRateRequest.service_provider_id,AirFreightRateRequest.performed_by_id,AirFreightRateRequest.performed_by_type,AirFreightRateRequest.performed_by_org_id)
        .where(
            AirFreightRateRequest.id << request.get("air_freight_rate_request_ids"),
            AirFreightRateRequest.status == "active",
        )
    )

    if not request_objects:
        raise HTTPException(
            status_code=404, detail="Invalid Rate Request"
        )

    air_freight_rate = None
    shipment_source = False
    for request_object in request_objects:
        if request_object.source == 'shipment' and request_object.source_id:
            shipment_source = True
            air_freight_rates = (
                AirFreightRate.select(AirFreightRate.validities,AirFreightRate.airline_id,AirFreightRate.service_provider_id,
                                        AirFreightRate.price_type,AirFreightRate.operation_type)
                .where(AirFreightRate.id == request.get("rate_id"))
            )
            air_freight_rates =jsonable_encoder(list(air_freight_rates.dicts()))
            if len(air_freight_rates):
                air_freight_rate = air_freight_rates[0]
                validities = air_freight_rate['validities']
                air_freight_rate['validities'] = []
                for validity in validities:
                    validity = {key:value for key,value in validity.items() if key in ["id","validity_end","weight_slabs","validity_start","min_price"] }
                    air_freight_rate['validities'].append(validity)
                break
    requests_objects = jsonable_encoder(list(request_objects.dicts()))

    for request_object in request_objects:
        request_object.status = "inactive"
        request_object.closed_by_id = request.get("performed_by_id")
        if request.get("closing_remarks"):
            request_object.closing_remarks = request.get("closing_remarks")
        
        try:
            request_object.save()
        except Exception as e:
            HTTPException(status_code = 400,detail = "Request Didn't Save")

        AirServiceAudit.create(**get_audit_params(request, request_object.id))

        id = str(request_object.performed_by_org_id)
        org_users = get_organization_partner(id)

        
        if org_users and request_object.performed_by_type == 'user' and request_object.source != 'checkout':
          send_closed_notifications_to_user_request.apply_async(
            kwargs={"object": request_object}, queue="critical"
        ) 

        else:
           send_closed_notifications_to_sales_agent_function.apply_async(
            kwargs={"object": request_object}, queue="critical"
        )

    if shipment_source:
        data = {
        'air_freight_rate_requests': requests_objects,
        }
        if air_freight_rate:
            data['air_freight_rate'] = air_freight_rate
            data['validity_id'] = request.get('validity_id')
        shipment_updation = shipment.update_sell_and_buy_quotations_for_air_freight_request(data)
        if not shipment_updation:
            return HTTPException(status_code = 400, detail = 'Request Not Closed')

    return {"air_freight_rate_request_ids": request.get("air_freight_rate_request_ids")}



def get_audit_params(request, request_object_id):
    data = {
        key: value
        for key, value in request.items()
        if key not in ["air_freight_rate_request_ids"]
    }

    return {
        "action_name": "delete",
        "performed_by_id": request.get("performed_by_id"),
        "data": data,
        "object_type": "AirFreightRateRequest",
        "object_id": request_object_id,
    }
