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
    cost_booking_data = get_cost_booking_data('79b677ac-e075-47a4-8f99-bfa2cda5e55b','eb187b38-51b2-4a5e-9f3c-978033ca1ddf',codes)
    print(cost_booking_data)
    return cost_booking_data
   