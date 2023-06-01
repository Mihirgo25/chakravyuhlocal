from database.rails_db import get_cost_booking_data

def get_cost_booking_transformation():
    codes=['locked', 'coe_approved']
    cost_booking_data = get_cost_booking_data('79b677ac-e075-47a4-8f99-bfa2cda5e55b','eb187b38-51b2-4a5e-9f3c-978033ca1ddf',codes)
    print(cost_booking_data)
    return cost_booking_data
   