from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from database.db_session import db
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_RATE_TYPE, DEFAULT_MODE
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit

def create_audit(request, freight_id,validity_id):
    request = { key: value for key, value in request.items() if value }
    audit_data = {}
    audit_data["validity_start"] = request.get("validity_start").isoformat()
    audit_data["validity_end"] = request.get("validity_end").isoformat()
    audit_data["performed_by_id"] = request.get("performed_by_id")
    audit_data["procured_by_id"] = request.get("procured_by_id")
    audit_data["sourced_by_id"] = request.get("sourced_by_id")
    audit_data["currency"] = request.get("currency")
    audit_data["price_type"] = request.get("price_type")
    audit_data["air_freight_rate_request_id"] = request.get("air_freight_rate_request_id")

    id = AirFreightRateAudit.create(
        bulk_operation_id=request.get("bulk_operation_id"),
        rate_sheet_id=request.get("rate_sheet_id"),
        action_name="create",
        performed_by_id=request["performed_by_id"],
        data=audit_data,
        object_id=freight_id,
        object_type="AirFreightRate",
        source=request.get("source"),
        validity_id=validity_id
    )
    return id

def create_air_freight_rate(request):
    with db.atomic():
        return create_air_freight_rate_data(request)

    
def create_air_freight_rate_data(request):
    from celery_worker import create_saas_air_schedule_airport_pair_delay, update_air_freight_rate_details_delay,update_multiple_service_objects

    if request['commodity']=='general':
        if request.get('commodity_sub_type'):
            request['commodity_sub_type']= request.get('commodity_sub_type')
        else:
            request['commodity_sub_type']='all'
    if request['density_category']=='general':
        request['density_ratio']='1:1'
    if request['commodity'] in ['dangerous goods','temperature control','special_consideration'] and not request.get('commodity_sub_type'):
        raise HTTPException(status_code=400, detail="Commodity Sub Type is required for {}".format(request['commodity']))
    
    if request.get('density_ratio') and request['density_ratio'].split(':')[0]!= '1':
        raise HTTPException(status_code=400,detail='Ratio should be in the form of 1:x')
    if len(set(slab['currency'] for slab in request['weight_slabs']))!=1 or request['weight_slabs'][0]['currency'] != request['currency']:
        raise HTTPException(status_code=400, detail='The Currency Entered in the weight Slabs doesnt match with Rate Currency')
    
    
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
        "rate_not_available_entry": request.get("rate_not_available_entry", False),
        "stacking_type":request.get("stacking_type"),
        "shipment_type":request.get("shipment_type"),
        "operation_type":request.get("operation_type"),
        "source": request.get("source", DEFAULT_MODE),
        "accuracy":request.get("accuracy", 100),
        "cogo_entity_id":request.get("cogo_entity_id"),
        "rate_type":request.get("rate_type", DEFAULT_RATE_TYPE),
        "price_type":price_type
    }

    init_key = f'{str(request.get("origin_airport_id"))}:{str(row["destination_airport_id"])}:{str(row["commodity"])}:{str(row["airline_id"])}:{str(row["service_provider_id"])}:{str(row["shipment_type"])}:{str(row["stacking_type"])}:{str(row["cogo_entity_id"] )}:{str(row["commodity_type"])}:{str(row["commodity_sub_type"])}:{str(row["price_type"])}:{str(row["rate_type"])}:{str(row["operation_type"])}:{str(row["source"])}'

    freight = (AirFreightRate.select().where(AirFreightRate.init_key == init_key).first())
   
    if not freight:
        freight = AirFreightRate(init_key = init_key)
        for key in list(row.keys()):
            setattr(freight, key, row[key])

        freight.set_locations()

        freight.set_origin_location_ids()

        freight.set_destination_location_ids()

    freight.sourced_by_id = request.get("sourced_by_id")
    freight.procured_by_id = request.get("procured_by_id")
    if 'rate_sheet_validation' not in request:
        freight.validate_validity_object(request.get('validity_start'),request.get('validity_end'))

    validity_id,weight_slabs = freight.set_validities(  
        request.get("validity_start").date(),
        request.get("validity_end").date(),
        request.get("min_price"),
        request.get("currency"),
        request.get("weight_slabs"),
        False,
        None,
        request.get("density_category"),
        request.get("density_ratio"),
        request.get("initial_volume"),
        request.get("initial_gross_weight"),
        request.get("available_volume"),
        request.get("available_gross_weight"),
        request.get("rate_type")
    )
    if request.get("source") == 'cargo_ai':   
        freight.add_flight_and_external_uuid(validity_id,request.get("flight_uuid"),request.get("external_rate_id"))

    freight.set_last_rate_available_date()

    set_object_parameters(freight, request)
    
    if 'rate_sheet_validation' not in request:
        freight.validate_before_save()

    freight.update_foreign_references(row['price_type'])
    
    try:
        freight.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Rate did not save")
    
    create_audit(request, freight.id,validity_id)

    create_saas_air_schedule_airport_pair_delay.apply_async(kwargs={'air_object':freight,'request':request},queue='low')

    update_multiple_service_objects.apply_async(kwargs={'object':freight},queue='low')

    freight.create_trade_requirement_rate_mapping(request.get('procured_by_id'), request['performed_by_id'])

    if request.get('air_freight_rate_request_id'):
        update_air_freight_rate_details_delay.apply_async(kwargs={ 'request':request }, queue='fcl_freight_rate')

    freight_object = {
        "id": freight.id,
        "validity_id":validity_id
    }
    return freight_object
    
def set_object_parameters(freight, request):
    freight.maximum_weight = request.get('maximum_weight')
    freight.length = request.get('length')
    freight.breadth = request.get('breadth')
    freight.height = request.get('height')
    freight.weight_slabs = request.get('weight_slabs')
    freight.rate_not_available_entry = False
    freight.currency = request.get('currency')