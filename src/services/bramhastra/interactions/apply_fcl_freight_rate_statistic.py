from services.bramhastra.helpers.fcl_freight import Rate


def apply_fcl_freight_rate_statistic(request):
    if request.create_params:
        create_fcl_freight_rate_statistic(request.action, request.create_params)
    elif request.update_params:
        update_fcl_freight_rate_statistic(request.action, request.update_params)
    else:
        raise ValueError("Send create or update freight parameters")


def create_fcl_freight_rate_statistic(action, params):
    rate = Rate(freight=params.freight)
    rate.set_formatted_data()

    if action == "create":
        rate.set_new_stats()


def update_fcl_freight_rate_statistic(action, params):
    pass
