from database.rails_db import get_cost_booking_data

def get_cost_booking_transformation(origin_port_id,destination_port_id):
    codes=['locked', 'coe_approved']
    cost_booking_data = get_cost_booking_data(origin_port_id,destination_port_id,codes)
    return cost_booking_data
   