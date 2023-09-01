from services.bramhastra.helpers.air_freight_rate_statistic_helper import Rate
from configs.env import APP_ENV

def apply_air_freight_rate_statistic(request):
    if APP_ENV == "production":
        setting_air_freight_rate_statistic(request.action, request.params)


def setting_air_freight_rate_statistic(action, params):
    rate = Rate(freight=params.freight)

    rate.set_formatted_data()

    if action == "create":
        rate.set_new_stats()
    elif action == "update":
        rate.set_existing_stats()
