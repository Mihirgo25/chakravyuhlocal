from database.db_session import db
from datetime import datetime, timedelta
from services.air_freight_rate.models.air_freight_rate_request import (
    AirFreightRateRequest,
)
from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from micro_services.client import shipment
from celery_worker import send_closed_notifications_to_sales_agent_function


def delete_air_freight_rate_request(request):
    object_type = "Air_Freight_Rate_Request"
    query = "create table if not exists air_services_audits{} partition of air_services_audits for values in ('{}')".format(
        object_type.lower(), object_type.replace("_", "")
    )
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    request_objects = (
        AirFreightRateRequest.select()
        .where(
            AirFreightRateRequest.id << request.get("air_freight_rate_request_ids"),
            AirFreightRateRequest.status == "active",
        )
        .execute()
    )

    if not request_objects:
        raise HTTPException(
            status_code=400, detail="air_freight_rate_request_ids are invalid"
        )

    for request_object in request_objects:
        request_object.status = "inactive"
        request_object.closed_by_id = request.get("performed_by_id")
        if request.get("closing_remarks"):
            request_object.closing_remarks = request.get("closing_remarks")
        if request_object.source == "shipment" and request_object.source_id:
            air_freight_rate = (
                AirFreightRate.select()
                .where(AirFreightRate.id == request.get("rate_id"))
                .first()
            )
            if not air_freight_rate:
                continue
            air_freight_rate_validity = None
            for validity in air_freight_rate.validities:
                if validity["id"] == request.get("validity_id"):
                    air_freight_rate_validity = validity
            if air_freight_rate_validity:
                if is_valid_params(
                    air_freight_rate, air_freight_rate_validity, request_object
                ) and collection_parties_present(request_object):
                    update_buy_line_items(air_freight_rate_validity, request_object)

            request_object.save()

            AirServiceAudit.create(**get_audit_params(request, request_object.id))

            send_closed_notifications_to_sales_agent_function.apply_async(
                kwargs={"object": request_object}, queue="low"
            )

    return {"air_freight_rate_request_ids": request.get("air_freight_rate_request_ids")}


def is_valid_params(
    air_freight_rate, air_freight_rate_validity, air_freight_rate_request
):
    return (
        air_freight_rate_validity
        and air_freight_rate.airline_id == air_freight_rate_request.airline_id
        and air_freight_rate.service_provider_id
        == air_freight_rate_request.service_provider_id
        and air_freight_rate.price_type == air_freight_rate_request.price_type
        and air_freight_rate.operation_type == air_freight_rate_request.operation_type
    )


def collection_parties_present(request_object):
    params = {
        "filters": {
            "service_provider_id": request_object.service_provider_id,
            "shipment_id": request_object.source_id,
        },
        "pagination_data_required": False,
        "page_limit": MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT,
    }
    req_collection_party = shipment.list_shipment_collection_party(params)["list"]

    if req_collection_party[0]["collection_parties"]:
        return False
    return True


def update_buy_line_items(air_freight_rate_validity, obj):
    params = {
        "shipment_id": str(obj.source_id),
        "service_detail_required": True,
        "performed_by_user_type": "agent",
    }
    shipment_quotations = shipment.get_shipment_services_quotation(params)[
        "service_charges"
    ]
    if shipment_quotations:
        air_freight_service_quotation = [
            shipment_quotation
            for shipment_quotation in shipment_quotations
            if shipment_quotation["service_type"] == "air_freight_service"
        ][0]
        BAS_CHARGE_CODES = ["BAS", "BASNO"]
        buy_line_items = air_freight_service_quotation["line_items"]
        for line_item in buy_line_items:
            if line_item["code"] in BAS_CHARGE_CODES:
                bas_buy_line_item = line_item
                break
        air_freight_service_detail = air_freight_service_quotation["service_detail"][0]
        chargeable_weight = air_freight_service_detail["chargeable_weight"]
        cargo_handed_over_date = air_freight_service_detail[
            "cargo_handed_over_at_origin_at"
        ]
        if not cargo_handed_over_date or ~(
            datetime.strptime(air_freight_rate_validity["validity_start"], "%Y-%m-%d")
            <= cargo_handed_over_date + timedelta(days=1)
            and cargo_handed_over_date + timedelta(days=1)
            <= datetime.strptime(air_freight_rate_validity["validity_end"]),
            "%Y-%m-%d",
        ):
            return
        required_weight_slab = {}
        for weight_slab in air_freight_rate_validity["weight_slabs"]:
            if int(weight_slab["lower_limit"]) <= int(chargeable_weight) and int(
                weight_slab["upper_limit"]
            ) > int(chargeable_weight):
                required_weight_slab = weight_slab
                break

        if required_weight_slab:
            bas_buy_line_item["price"] = required_weight_slab.get("tariff_price")
            bas_buy_line_item["currency"] = required_weight_slab.get("currency")
            params = {
                "quotations": [
                    {
                        "id": air_freight_service_quotation.get("id"),
                        "service_id": air_freight_service_quotation.get("service_id"),
                        "line_items": [bas_buy_line_item],
                    }
                ]
            }

            response = shipment.update_shipment_buy_quotations(params)
            if "ids" not in response:
                raise HTTPException(
                    status_code=400, detail="COULD NOT UPDATE BUY QUOTATION"
                )
        else:
            raise HTTPException(status_code=404, detail="Weight Slab not consistent")


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
