from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.postgres_ext import *
from database.db_session import db

def execute(request):
    if all_fields_present:
        return {}
    object=find_object
    if not object:
        return {}
    
    freight_object=None
    if request['weight']:
        validities=object.validities
        for validity in validities:
            