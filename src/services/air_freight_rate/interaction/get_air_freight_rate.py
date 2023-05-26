from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.postgres_ext import *
# from database.db_session import db
from operator import attrgetter



def get_air_freight_rate(request):
    if  not all_fields_present(request):
        return {}
    
    object=find_object(request)
    if  not object :
        return {}
    
    freight_object=None
    if request['weight']:
        validities=object['validities']
        for validity in validities:
            freight_object=build_freight_object(validity,request)
            if not freight_object:
                continue
            break



def build_freight_object(freight_validity,request):
    if freight_validity['validity_start'] > request.get('validity_end') or freight_validity['validity_end']<request.get('validity_start') or  request.get('cargo_readiness_date') < freight_validity['validity_start'] or request.get('cargo_readiness_date') > freight_validity['validity_end']:
        return None

    freight_object={
        'validity_start':freight_validity.get('validity_start'),
        'validity_end':freight_validity.get('validity_end'),
        "validity_id":freight_validity.get('validity_id'),
        "likes_count":freight_validity.get('likes_count'),
        "dislikes_count":freight_validity.get('dislikes_count'),
        'line_items':[]
    }
    if freight_object['validity_start'] < request.get('validity_start'):
        freight_object['validity_start'] = request.get('validity_start') 
    if freight_object['validity_end'] > request.get('validity_end'):
        freight_object['validity_end'] = request.get('validity_end') 






    origin_local_object_params = {
        'airport_id': request.get('airport_id'),
        'airline_id': request.get('airline_id'),
        'trade_type': 'export',
        'commodity':request.get('commodity'),
        'service_provider_id': request.get('service_provider_id'),
    }
    destination_local_object_params = {
        'airport_id': request.get('airport_id'),
        'airline_id': request.get('airline_id'),
        'trade_type': 'import',
        'commodity':request.get('commodity'),
        'service_provider_id': request.get('service_provider_id'),
    }
    get_surcharge_object_params = {
        'origin_airport_id': request.get('origin_airport_id'),
        'destination_airport_id': request.get('destination_airport_id'),
        'airline_id': request.get('airline_id'),
        'commodity':request.get('commodity'),
        'operation_type': request.get('operation_type'),
        'service_provider_id':request.get('service_provider_id')
    }

def all_fields_present(request):
    if ((request.get('origin_airport_id') is not None) and (request.get('destination_airport_id')is not None) and (request.get('commodity')is not None )and (request.get('airline_id') is not None)and (request.get('operation_type')is not None)and (request.get('service_provider_id')is not None)and (request.get('price_type')is not None)):
        return True
    return False


def find_object(request):
  query = AirFreightRate.select()
  for key in request:
    query = query.where(attrgetter(key)(AirFreightRate) == request[key])
  object = query.first()
  
  return object


