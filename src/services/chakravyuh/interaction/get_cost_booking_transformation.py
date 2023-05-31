from database.db_session import db
from fastapi.exceptions import HTTPException
from database.rails_db import get_cost_booking_data
from datetime import datetime,timedelta
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

def get_cost_booking_transformation():
    with db.atomic():
        return transaction()
    
def transaction():
    # from celery_worker import adjust_fcl_freight_dynamic_pricing
    codes=['locked', 'coe_approved']
    cost_booking_data = get_cost_booking_data('1b94734e-7d51-4e94-9dd2-ef96aee64a8f','541d1232-58ce-4d64-83d6-556a42209eb7',codes)
    print(cost_booking_data)
    return cost_booking_data
   