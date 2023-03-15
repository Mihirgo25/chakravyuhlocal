from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import json
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from rails_client import client
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize
from celery_worker import delay_fcl_functions
from datetime import datetime
from database.db_session import db


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


def create_audit(request, freight_id):

    audit_data = {}
    audit_data["validity_start"] = request["validity_start"].isoformat()
    audit_data["validity_end"] = request["validity_end"].isoformat()
    audit_data["line_items"] = request["line_items"]
    audit_data["weight_limit"] = request["weight_limit"]
    audit_data["origin_local"] = request.get("origin_local")
    audit_data["destination_local"] = request.get("destination_local")
    audit_data["is_extended"] = request.get("is_extended")

    FclFreightRateAudit.create(
        bulk_operation_id=request.get("bulk_operation_id"),
        rate_sheet_id=request.get("rate_sheet_id"),
        action_name="create",
        performed_by_id=request["performed_by_id"],
        procured_by_id=request["procured_by_id"],
        sourced_by_id=request["sourced_by_id"],
        data=audit_data,
        object_id=freight_id,
        object_type="FclFreightRate",
        source=request.get("source"),
    )


def create_fcl_freight_rate_data(request):
    row = {
        "origin_main_port_id": request.get("origin_main_port_id"),
        "destination_port_id": request.get("destination_port_id"),
        "destination_main_port_id": request.get("destination_main_port_id"),
        "container_size": request.get("container_size"),
        "container_type": request.get("container_type"),
        "commodity": request.get("commodity"),
        "shipping_line_id": request.get("shipping_line_id"),
        "service_provider_id": request.get("service_provider_id"),
        "importer_exporter_id": request.get("importer_exporter_id"),
        "cogo_entity_id": request.get("cogo_entity_id"),
        "sourced_by_id": request.get("sourced_by_id"),
        "procured_by_id": request.get("procured_by_id"),
    }

    init_key = f'{str(request.get("origin_port_id"))}:{str(row["origin_main_port_id"] or "")}:{str(row["destination_port_id"])}:{str(row["destination_main_port_id"] or "")}:{str(row["container_size"])}:{str(row["container_type"])}:{str(row["commodity"])}:{str(row["shipping_line_id"])}:{str(row["service_provider_id"])}:{str(row["importer_exporter_id"] or "")}:{str(row["cogo_entity_id"] or "")}'
    
    freight = (
        FclFreightRate.select()
        .where(
            FclFreightRate.origin_port_id == request.get("origin_port_id"),
            FclFreightRate.init_key == init_key,
        )
        .first()
    )
    
    if not freight:
        freight = FclFreightRate(origin_port_id = request.get('origin_port_id'), init_key = init_key)
        for key in list(row.keys()):
            setattr(freight, key, row[key])
        freight.set_locations()
        freight.set_origin_location_ids()
        freight.set_destination_location_ids()

    freight.sourced_by_id = request.get("sourced_by_id")
    freight.procured_by_id = request.get("procured_by_id")
    

    freight.weight_limit = to_dict(request.get("weight_limit"))

    origin_local = {
        k: v
        for k, v in request.get("origin_local", {}).items()
        if k not in ["detention", "demurrage"]
    }
    destination_local = {
        k: v
        for k, v in request.get("destination_local", {}).items()
        if k not in ["detention", "demurrage"]
    }

    if freight.origin_local and request.get("origin_local"):
        freight.origin_local.update(origin_local)
    elif request.get("origin_local"):
        freight.origin_local = origin_local
    else:
        freight.origin_local = {"line_items": [], "plugin": None}

    if freight.destination_local and request.get("destination_local"):
        freight.destination_local.update(destination_local)
    elif request.get("destination_local"):
        freight.destination_local = destination_local
    else:
        freight.destination_local = {"line_items": [], "plugin": None}

    freight.origin_detention = request.get("origin_local", {}).get("detention", {})
    freight.origin_demurrage = request.get("origin_local", {}).get("demurrage", {})
    freight.destination_detention = request.get("destination_local", {}).get(
        "detention", {}
    )
    freight.destination_demurrage = request.get("destination_local", {}).get(
        "demurrage", {}
    )

    freight.validate_validity_object(request["validity_start"], request["validity_end"])

    freight.validate_line_items(to_dict(request.get("line_items")))

    freight.set_validities(
        request["validity_start"].date(),
        request["validity_end"].date(),
        to_dict(request["line_items"]),
        request["schedule_type"],
        False,
        request["payment_term"],
    )

    freight.set_platform_prices()
    freight.set_is_best_price()
    freight.set_last_rate_available_date()
    freight.validate_before_save()

    try:
        freight.save()
    except Exception as e:
        print("Exception in saving freight rate", str(e))
        if 'no partition of relation "fcl_freight_rates" found for row' in str(e):
            origin_port_id = str(request.get("origin_port_id"))
            query = "create table fcl_freight_rates_{} partition of fcl_freight_rates for values in ('{}')".format(origin_port_id.replace("-", "_"), origin_port_id)
            db.execute_sql(query)
            freight.save()
        else:
            raise HTTPException(status_code=499, detail="rate did not save")

    # freight.create_fcl_freight_free_days(freight.origin_local, freight.destination_local, request['performed_by_id'], request['sourced_by_id'], request['procured_by_id'])

    # if not request.get('importer_exporter_id'):
    #   freight.delete_rate_not_available_entry()

    # create_audit(request, freight.id)

    # freight.update_special_attributes()

    # freight.update_local_references()

    # freight.update_platform_prices_for_other_service_providers()

  delay_fcl_functions.apply_async(kwargs={'fcl_object':freight,'request':request},queue='low')

  return {"id": freight.id}

