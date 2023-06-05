from database.rails_db import get_past_cost_booking_data
from services.chakravyuh.setters.fcl_booking_invoice import FclBookingVyuh as FclBookingVyuhSetters
def get_cost_booking_transformation():
    codes=['locked', 'coe_approved']
    cost_booking_data = get_past_cost_booking_data()
    for booking_data in cost_booking_data:
            setter = FclBookingVyuhSetters(booking_data)
            setter.set_dynamic_pricing()
    return cost_booking_data
   