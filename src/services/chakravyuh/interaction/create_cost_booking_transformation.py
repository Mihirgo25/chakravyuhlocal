from database.db_session import db
from fastapi.exceptions import HTTPException
from database.rails_db import get_cost_booking_data
from datetime import datetime,timedelta
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

def create_cost_booking_transformation():
    with db.atomic():
        return transaction()
    
def transaction():
    from celery_worker import adjust_fcl_freight_dynamic_pricing
    codes=['locked', 'coe_approved']
    cost_booking = get_cost_booking_data('1b94734e-7d51-4e94-9dd2-ef96aee64a8f','541d1232-58ce-4d64-83d6-556a42209eb7',codes)
    print('cost_booking',cost_booking)
    validity_start =  datetime.now().date()
    validity_end = str(validity_start + timedelta(days=7))
    validity_start=str(validity_start)
    for rates in cost_booking:
        current_validities=[{'validity_start':validity_start,'validity_end':validity_end,'line_items':rates['line_items']}]
        print('current_validities',current_validities)
        rates['rate_type']='market_place'
        rates['mode']='manual'
        rates['schedule_type']=None
        rates['payment_term']=None
        rates['commodity']=None
        adjust_fcl_freight_dynamic_pricing(rates, current_validities)

        # adjust_fcl_freight_dynamic_pricing.apply_async(kwargs={ 'new_rate':rates , 'current_validities': current_validities }, queue='low')