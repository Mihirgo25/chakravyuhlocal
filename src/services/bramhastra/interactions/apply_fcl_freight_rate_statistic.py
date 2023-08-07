from services.bramhastra.helpers.post_fcl_freight_helper import Rate


def apply_fcl_freight_rate_statistic(request):
    setting_fcl_freight_rate_statistic(request.action, request.params)


def setting_fcl_freight_rate_statistic(action, params):
    rate = Rate(freight=params.freight)
    
    rate.set_non_existing_location_details()
    
    rate.set_formatted_data()

    if action == "create":
        rate.set_new_stats()
    elif action == "update":
        rate.set_existing_stats()