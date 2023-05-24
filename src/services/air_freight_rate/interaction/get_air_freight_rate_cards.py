from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.postgres_ext import *

def get_air_freight_rate_cards(request):
    if request['commodity'] =='general':
        request['commodity_subtype'] = 'all'
    
    if request['commodity'] == 'special_consideration' and not request.get('commodity_subtype'):
        raise HTTPException(status_code=400, detail="commodity_sub_type is required for special_consideration")

    freight_query = initialize_freight_query(request)


def initialize_freight_query(request):
    return
    

