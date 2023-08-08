from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate_properties import FclFreightRateProperties
from services.fcl_freight_rate.interaction.get_suggested_cogo_assured_fcl_freight_rates import add_suggested_validities
from database.db_session import db
from fastapi.encoders import jsonable_encoder
from configs.global_constants import HAZ_CLASSES
from datetime import datetime
from services.fcl_freight_rate.helpers.get_normalized_line_items import get_normalized_line_items
from configs.fcl_freight_rate_constants import VALUE_PROPOSITIONS, DEFAULT_RATE_TYPE, EXTENSION_ENABLED_MODES
from configs.env import DEFAULT_USER_ID
from services.fcl_freight_rate.helpers.rate_extension_via_bulk_operation import rate_extension_via_bulk_operation
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects

def add_rate_properties(request,freight_id):
    validate_value_props(request["value_props"])
    rp = FclFreightRateProperties.select(FclFreightRateProperties.id).where(FclFreightRateProperties.rate_id == freight_id).first()
    if not rp :
        FclFreightRateProperties.create(
            rate_id = freight_id,
            created_at = datetime.now(),
            updated_at = datetime.now(),
            value_props = request["value_props"],
            t_n_c = request["t_n_c"],
            available_inventory = request["available_inventory"],
            used_inventory = request.get("used_inventory"),
            shipment_count = request["shipment_count"],
            volume_count=request["volume_count"]
        )
    # rp = FclFreightRateProperties.select().where(FclFreightRateProperties.rate_id == freight_id).first()
    # rp.validate_value_props()


def create_audit(request, freight_id):

    rate_type = request.get('rate_type')

    audit_data = {}
    audit_data["validity_start"] = request["validity_start"].isoformat()
    audit_data["validity_end"] = request["validity_end"].isoformat()
    audit_data["line_items"] = request.get("line_items")
    audit_data["weight_limit"] = request.get("weight_limit")
    audit_data["origin_local"] = request.get("origin_local")
    audit_data["destination_local"] = request.get("destination_local")
    audit_data["is_extended"] = request.get("is_extended")
    audit_data["fcl_freight_rate_request_id"] = request.get("fcl_freight_rate_request_id")
    audit_data['validities'] = jsonable_encoder(request.get("validities") or {}) if rate_type == 'cogo_assured' else None
    audit_data['sourced_by_id'] = str(request.get("sourced_by_id"))
    audit_data['payment_term'] = request.get("payment_term")
    audit_data['schedule_type'] = request.get("schedule_type")
    audit_data['procured_by_id'] = str(request.get("procured_by_id"))

    id = FclFreightRateAudit.create(
        bulk_operation_id=request.get("bulk_operation_id"),
        rate_sheet_id=request.get("rate_sheet_id"),
        action_name="create",
        performed_by_id=request["performed_by_id"],
        data=audit_data,
        object_id=freight_id,
        object_type="FclFreightRate",
        source=request.get("source"),
        extended_from_object_id=request.get('extended_from_object_id'),
        performed_by_type = request.get("performed_by_type") or "agent"
    )
    return id

def create_fcl_freight_rate_data(request):
    # origin_port_id = str(request.get("origin_port_id"))
    # query = "create table if not exists fcl_freight_rates_{} partition of fcl_freight_rates for values in ('{}')".format(origin_port_id.replace("-", "_"), origin_port_id)
    # db.execute_sql(query)
    with db.atomic():
      return create_fcl_freight_rate(request)

def create_fcl_freight_rate(request):
    from celery_worker import delay_fcl_functions, update_fcl_freight_rate_request_in_delay, update_fcl_freight_rate_feedback_in_delay
    request = { key: value for key, value in request.items() if value }
    row = {
        'origin_port_id': request.get('origin_port_id'),
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
        "mode": request.get("mode") or request.get("source") or "manual",
        "accuracy":request.get("accuracy", 100),
        "payment_term": request.get("payment_term", "prepaid"),
        "schedule_type": request.get("schedule_type", "direct"),
        "rate_not_available_entry": request.get("rate_not_available_entry", False),
        "rate_type": request.get("rate_type", DEFAULT_RATE_TYPE)
    }
    init_key = f'{str(request.get("origin_port_id"))}:{str(row["origin_main_port_id"] or "")}:{str(row["destination_port_id"])}:{str(row["destination_main_port_id"] or "")}:{str(row["container_size"])}:{str(row["container_type"])}:{str(row["commodity"])}:{str(row["shipping_line_id"])}:{str(row["service_provider_id"])}:{str(row["importer_exporter_id"] or "")}:{str(row["cogo_entity_id"] or "")}'
    freight = (
        FclFreightRate.select()
        .where(
            FclFreightRate.init_key == init_key,
            FclFreightRate.rate_type == row['rate_type']
        )
        .first()
    )
    
    is_new_rate = False
    
    if not freight:
        is_new_rate = True
        freight = FclFreightRate(init_key = init_key)
        for key in list(row.keys()):
            setattr(freight, key, row[key])

    freight.set_locations()
    freight.set_origin_location_ids()
    freight.set_destination_location_ids()
    freight.sourced_by_id = request.get("sourced_by_id")
    freight.procured_by_id = request.get("procured_by_id")


    freight.weight_limit = request.get("weight_limit")

    new_free_days = {}

    new_free_days['origin_detention'] = request.get("origin_local", {}).get("detention", {})
    new_free_days['origin_demurrage'] = request.get("origin_local", {}).get("demurrage", {})
    new_free_days['destination_detention'] = request.get("destination_local", {}).get("detention", {})
    new_free_days['destination_demurrage'] = request.get("destination_local", {}).get("demurrage", {})

    if request.get("origin_local") and "line_items" in request["origin_local"]:
        freight.origin_local = {
            "line_items": get_normalized_line_items(request["origin_local"]["line_items"])
        }
    else:
        freight.origin_local = { "line_items": [] }

    if request.get("destination_local") and "line_items" in request["destination_local"]:
        freight.destination_local = {
            "line_items": get_normalized_line_items(request["destination_local"]["line_items"])
        }
    else:
        freight.destination_local = { "line_items": [] }

    source = request.get("source")
    line_items = get_flash_booking_rate_line_items(request) if source == "flash_booking" else request.get("line_items") 

    line_items = get_normalized_line_items(line_items)

    if 'rate_sheet_validation' not in request and row['rate_type'] != "cogo_assured":
        freight.validate_validity_object(request["validity_start"], request["validity_end"])
        freight.validate_line_items(line_items)

    if row["rate_type"] == "cogo_assured":
        freight.set_validities_for_cogo_assured_rates(request['validities'])
    else:
        freight.set_validities(
            request["validity_start"].date(),
            request["validity_end"].date(),
            line_items,
            request.get("schedule_type"),
            False,
            request.get("payment_term"),
            request.get('tag')
        )

    freight.set_platform_prices(row["rate_type"])
    freight.set_is_best_price()

    freight.set_last_rate_available_date()
    
    if 'rate_sheet_validation' not in request:
        freight.validate_before_save()
    
    freight.create_fcl_freight_free_days(new_free_days, request['performed_by_id'], request['sourced_by_id'], request['procured_by_id'])

    freight.update_special_attributes()

    freight.update_local_references()  

    try:
        freight.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="rate did not save")

    if row['rate_type'] == 'cogo_assured':
        try:
            add_rate_properties(request,freight.id)
        except Exception as e:
            print(e)
    
    # adjust_cogoassured_price(row, request)    
    
    create_audit(request, freight.id)
    
    if not request.get('importer_exporter_id') and not request.get("rate_not_available_entry"):
      freight.delete_rate_not_available_entry()
    
    freight.update_platform_prices_for_other_service_providers()

    is_rate_extended_via_bo = rate_extension_via_bulk_operation(request)
    
    get_multiple_service_objects(freight, is_new_rate)

    delay_fcl_functions.apply_async(kwargs={'request':request},queue='low')
     
    current_validities = freight.validities
    adjust_dynamic_pricing(request, row, freight, current_validities, is_rate_extended_via_bo)

    if request.get('fcl_freight_rate_request_id'):
        update_fcl_freight_rate_request_in_delay({'fcl_freight_rate_request_id': request.get('fcl_freight_rate_request_id'), 'closing_remarks': 'rate_added', 'performed_by_id': request.get('performed_by_id')})

    if request.get('fcl_freight_rate_feedback_id'):
        update_fcl_freight_rate_feedback_in_delay({'fcl_freight_rate_feedback_id': request.get('fcl_freight_rate_feedback_id'), 'reverted_validities': [{"line_items":request.get('line_items'), "validity_start":request["validity_start"].isoformat(), "validity_end":request["validity_end"].isoformat()}], 'performed_by_id': request.get('performed_by_id')})

    return {"id": freight.id}

def adjust_dynamic_pricing(request, row, freight: FclFreightRate, current_validities, is_rate_extended_via_bo):
    from celery_worker import extend_fcl_freight_rates, adjust_fcl_freight_dynamic_pricing
    rate_obj = request | row | { 
        'origin_location_ids': freight.origin_location_ids,
        'destination_location_ids': freight.destination_location_ids,
        'id': freight.id,
        'origin_country_id': freight.origin_country_id,
        'destination_country_id': freight.destination_country_id,
        'origin_trade_id': freight.origin_trade_id,
        'destination_trade_id': freight.destination_trade_id,
        'service_provider_id': freight.service_provider_id,
        'extend_rates_for_existing_system_rates': True
    }
    if row["mode"] in EXTENSION_ENABLED_MODES and not request.get("is_extended") and not is_rate_extended_via_bo and row['rate_type'] == "market_place":
        extend_fcl_freight_rates.apply_async(kwargs={ 'rate': rate_obj }, queue='low')
    
    if row["mode"] in EXTENSION_ENABLED_MODES and not request.get("is_extended") and row['rate_type'] == "market_place":
        adjust_fcl_freight_dynamic_pricing.apply_async(kwargs={ 'new_rate': rate_obj, 'current_validities': current_validities }, queue='low')

def adjust_cogoassured_price(row, request):
    from celery_worker import create_fcl_freight_rate_delay
    if row['rate_type'] != DEFAULT_RATE_TYPE:
        return
    
    cogo_id = FclFreightRate.select(FclFreightRate.id).where(
        FclFreightRate.origin_port_id == request.get('origin_port_id'),
        FclFreightRate.origin_main_port_id == request.get('origin_main_port_id'),
        FclFreightRate.destination_port_id == request.get('destination_port_id'),
        FclFreightRate.container_size == request.get('container_size'),
        FclFreightRate.commodity == request.get('commodity'),
        FclFreightRate.shipping_line_id == request.get('shipping_line_id'),
        FclFreightRate.service_provider_id == request.get('service_provider_id'),
        FclFreightRate.importer_exporter_id == request.get('importer_exporter_id'),
        FclFreightRate.cogo_entity_id == request.get('cogo_entity_id'),
        FclFreightRate.destination_port_id == request.get('destination_port_id'),
        FclFreightRate.rate_type == 'cogo_assured').first()

    if not cogo_id: 
        params = request
        params['rate_type'] = 'cogo_assured' 
        params['validities'] = validities_for_cogo_assured(params)
        create_fcl_freight_rate_delay.apply_async(kwargs={'request':params},queue='fcl_freight_rate')
    else:
        print('Update Cogoassured id')


def get_flash_booking_rate_line_items(request):
    line_items = request.get("line_items")
    if request['container_type'] in ['open_top', 'flat_rack', 'iso_tank'] or request['container_size'] == '45HC':
        line_items.append({
            "code": "SPE",
            "unit": "per_container",
            "price": 0,
            "currency": "USD",
            "remarks": [
            ],
            "slabs": []
        })
    
    if request['commodity'] in HAZ_CLASSES:
        line_items.append({
            "code": "HSC",
            "unit": "per_container",
            "price": 0,
            "currency": "USD",
            "remarks": [
            ],
            "slabs": []
        })
    return line_items

def validities_for_cogo_assured(request):
    input_param = {
        "container_size": request["container_size"],
        "price": request["line_items"][0]["price"],
        "currency": request["line_items"][0]["currency"]
    }
    validities = add_suggested_validities(input_param)
    return validities['validities']

def validate_value_props(v_props):
    for prop in v_props:
        name = prop.get('name')
        # print(name)
        if name not in VALUE_PROPOSITIONS:
            raise HTTPException(status_code=400, detail='Invalid rate_type parameter')   
    return True


    


