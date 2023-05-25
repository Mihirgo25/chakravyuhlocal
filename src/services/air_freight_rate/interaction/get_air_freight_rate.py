from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.postgres_ext import *
from database.db_session import db



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
    freight_object
    

