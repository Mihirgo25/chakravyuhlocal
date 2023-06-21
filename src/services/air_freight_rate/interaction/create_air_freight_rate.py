from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.postgres_ext import *
from database.db_session import db
import datetime
import pytz
from configs.air_freight_rate_constants import DEFAULT_RATE_TYPE
from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit

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

    id = AirFreightRateAudit.create(
        bulk_operation_id=request.get("bulk_operation_id"),
        rate_sheet_id=request.get("rate_sheet_id"),
        action_name="create",
        performed_by_id=request["performed_by_id"],
        data=audit_data,
        object_id=freight_id,
        object_type="FclFreightRate",
        source=request.get("source"),
    )
    return id

def create_air_freight_rate_data(request):
    with db.atomic():
        return create_air_freight_rate(request)

    
def create_air_freight_rate(request):
    from celery_worker import delay_air_functions, update_air_freight_rate_request_in_delay

    if request['commodity']=='general':
        request['commodity_sub_type']='all'
    if request['density_category']=='general':
        request['density_ratio']='1:1'
    if request['commodity'] == 'special_consideration' and not request.get('commodity_subtype'):
        raise HTTPException(status_code=400, detail="commodity_sub_type is required for special_consideration")
    if request.get('density_ratio') and request['density_ratio'].split(':')[0]!= '1':
        raise HTTPException(status_code='400',detail='should be in the form of 1:x')
    if len(set(slab['currency'] for slab in request['weight_slabs']))!=1 or request['weight_slabs'][0]['currency'] != request['currency']:
        raise HTTPException(status_code='400', detail='currency invalid')
    
    
    request['weight_slabs'] = sorted(request.get('weight_slabs'), key=lambda x: x['lower_limit'])


    if request.get('rate_type') in ["promotional" ,"consolidated"]:
        price_type="all_in"
    else:
        price_type=request.get('price_type')


    row = {
        'origin_airport_id': request.get('origin_airport_id'),
        "destination_airport_id": request.get("destination_airport_id"),
        "commodity": request.get("commodity"),
        "commodity_type":request.get("commodity_type"),
        "commodity_sub_type":request.get("commodity_sub_type"),
        "airline_id": request.get("airline_id"),
        "service_provider_id": request.get("service_provider_id"),
        "importer_exporter_id": request.get("importer_exporter_id"),
        "sourced_by_id": request.get("sourced_by_id"),
        "procured_by_id": request.get("procured_by_id"),
        "rate_not_available_entry": request.get("rate_not_available_entry", False),
        "stacking_type":request.get("stacking_type"),
        "shipment_type":request.get("shipment_type"),
        "operation_type":request.get("operation_type"),
        "mode": request.get("mode", "manual"),
        "accuracy":request.get("accuracy", 100),
        "cogo_entity_id":request.get("cogo_entity_id"),
        "rate_type":request.get("rate_type", DEFAULT_RATE_TYPE),
        "price_type":price_type
    }

    init_key = f'{str(request.get("origin_airport_id"))}:{str(row["destination_airport_id"])}:{str(row["commodity"])}:{str(row["airline_id"])}:{str(row["service_provider_id"])}:{str(row["importer_exporter_id"] or "")}:{str(row["shipment_type"])}:{str(row["stacking_type"])}:{str(row["cogo_entity_id"] )}'
    freight = (
        AirFreightRate.select()
        .where(
            AirFreightRate.init_key == init_key,
            AirFreightRate.rate_type == row['rate_type']
        )
        .first()
    )
   
    if not freight:
        freight = AirFreightRate(init_key = init_key)
        for key in list(row.keys()):
            setattr(freight, key, row[key])
        freight.set_locations()
        freight.set_origin_location_ids()
        freight.set_destination_location_ids()
    freight.sourced_by_id = request.get("sourced_by_id")
    freight.procured_by_id = request.get("procured_by_id")

    freight.validate_validity_object(request.get('validity_start'),request.get('validity_end'))
    
    if request.get('rate_sheet_id'):
        request['validity_start']  = pytz.timezone('Asia/Kolkata').localize(datetime.strptime(request.get('validity_start'), "%Y-%m-%d %H:%M:%S")).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.UTC)
        request['validity_end']  = pytz.timezone('Asia/Kolkata').localize(datetime.strptime(request.get('validity_end'), "%Y-%m-%d %H:%M:%S")).replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.UTC)

    validity_id = freight.set_validities(request.get("validity_start").date(),request.get("validity_end").date(),request.get("min_price"),request.get("currency"),request.get("weight_slabs"),False,None,request.get("density_category"),request.get("density_ratio"),request.get("initial_volume"),request.get("initial_gross_weight"),request.get("available_volume"),request.get("available_gross_weight"),request.get("rate_type"))
    freight.set_last_rate_available_date()
    set_object_parameters(freight, request)
    freight.validate_before_save()

    freight.update_foreign_references(row['price_type'])
    
    try:
        freight.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="rate did not save")
    
    create_audit(request, freight.id)

    delay_air_functions.apply_async(kwargs={'air_object':freight,'request':request},queue='low')
    freight.create_trade_requirement_rate_mapping(request.get('procured_by_id'), request['performed_by_id'])

    if request.get('air_freight_rate_request_id'):
        update_air_freight_rate_request_in_delay({'air_freight_rate_request_id': request.get('air_freight_rate_request_id'), 'closing_remarks': 'rate_added', 'performed_by_id': request.get('performed_by_id')})

    return {
        "id": freight.id,
        "validity_id":validity_id
    }
    


def set_object_parameters(freight, request):
    freight.maximum_weight = request.get('maximum_weight')
    freight.length = request.get('length')
    freight.breadth = request.get('breadth')
    freight.height = request.get('height')
    freight.weight_slabs = request.get('weight_slabs')
    freight.rate_not_available_entry = False
    freight.flight_uuid = request.get('flight_uuid')
    freight.external_rate_id = request.get('external_rate_id')
    freight.currency = request.get('currency')





    






