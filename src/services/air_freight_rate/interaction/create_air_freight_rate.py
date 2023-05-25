from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.postgres_ext import *
from database.db_session import db
import datetime

def create_air_freight_rate_data(request):
    with db.atomic():
        return create_air_freight_rate(request)

    
def create_air_freight_rate(request):
    if request['commodity']=='general':
        request['commodity_sub_type']='all'
    if request['desnity_category']=='genral':
        request['density_ratio']='1:1'
    if request['commodity'] == 'special_consideration' and not request.get('commodity_subtype'):
        raise HTTPException(status_code=400, detail="commodity_sub_type is required for special_consideration")
    if request['density_ratio']  and request['density_ratio']!= '1':
        raise HTTPException(status_code='400',detail='should be in the form of 1:x')
    if len(set(slab['currency'] for slab in request['weight_slabs']))!=1 or  request['weight_slabs'][0]['currency'] != request['currency']:
        raise HTTPException(status_code='400', detail='currency invalid')
    
    
    request['weight_slabs'] = sorted(request['weight_slabs'], key=lambda x: x['lower_limit'])

    if request['rate_type']=="promotional" or request['rate_type']=="consolidated":
        price_type="all_in"
    price_type="net_net"
    row = {
        'origin_airport_id': request.get('origin_airport_id'),
        "destination_airport_id": request.get("destination_airport_id"),
        "commodity": request.get("commodity"),
        "commodity_type":request.get("commodity_type"),
        "commodity_sub_type":request.get("commodity_sub_type"),
        "air_line_id": request.get("air_line_id"),
        "service_provider_id": request.get("service_provider_id"),
        "sourced_by_id": request.get("sourced_by_id"),
        "procured_by_id": request.get("procured_by_id"),
        "rate_not_available_entry": request.get("rate_not_available_entry", False),
        "stacking_type":request.get("stacking_type"),
        "shipment_type":request.get("shipment_type"),
        "operation_type":request.get("operation_type"),
        "price_type":request.get("price_type"),
        "source":request.get("source"),
        "cogo_entity_id":request.get("cogo_entity_id"),
        "rate_type":request.get("rate_type"),
        "price_type":price_type
    }

    init_key = f'{str(request.get("origin_airport_id"))}:{str(row["destination_airport_id"])}:{str(row["commodity"])}:{str(row["airline_line_id"])}:{str(row["service_provider_id"])}:{str(row["importer_exporter_id"] or "")}:{str(row["shipment_type"])}:{str(row["stacking_type"])}:{str(row["cogo_entity_id"] or "")}'
    freight = (
        AirFreightRate.select()
        .where(
            AirFreightRate.init_key == init_key,
        )
        .first()
    )

   
    if not freight:
        freight = AirFreightRate(init_key = init_key)
        for key in list(row.keys()):
            setattr(freight, key, row[key])

    freight.validate_validity_object(request['validity_start'],request['validity_end'])
    
    
    if request['rate_sheet_id']:
        request['validity_start'] = request['validity_start'].to_datetime.in_time_zone('Asia/Calcutta').beginning_of_day.utc
        request['validity_end'] = request['validity_end'].to_datetime.in_time_zone('Asia/Calcutta').end_of_day.utc

    validity_id=freight.set_validities(request.get("validity_start"),request.get("validity_end"),request.get("min_price"),request.get("currency"),request.get("weight_slabs"),False,None,request.get("density_category"),request.get("density_ratio"),request.get("initial_volume"),request.get("initial_gross_weight"),request.get("available_volume"),request.get("available_gross_weight"),request.get("rate_type"))


    






