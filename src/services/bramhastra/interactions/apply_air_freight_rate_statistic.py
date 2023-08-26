from services.bramhastra.helpers.post_air_freight_helper import Rate
# from playhouse.shortcuts import model_to_dict


def apply_air_freight_rate_statistic(request):
    if request.create_params:
        create_air_freight_rate_statistic(request.action, request.create_params)
    elif request.update_params:
        update_air_freight_rate_statistic(request.action, request.update_params)
    else:
        raise ValueError("Send create or update freight parameters")


def create_air_freight_rate_statistic(action, params):
    rate = Rate(freight=params.freight)
    rate.set_formatted_data()

    if action == "create":
        rate.set_new_stats()
    elif action == "update":
        rate.set_existing_stats()

def update_air_freight_rate_statistic(action, params):
    pass