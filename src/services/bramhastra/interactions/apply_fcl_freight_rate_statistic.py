from services.bramhastra.helpers.fcl_freight_rate_statistic_helper import Rate
from configs.env import APP_ENV


def apply_fcl_freight_rate_statistic(request):
    if APP_ENV == "production":
        setting_fcl_freight_rate_statistic(request.action, request.params)


def setting_fcl_freight_rate_statistic(action, params):
    rate = Rate(freight=params.freight)

    rate.set_pricing_map_zone_ids()

    if action == "delete":
        rate.delete_latest_stat()
        return

    rate.set_formatted_data()

    if action == "create":
        rate.set_new_stats()
    elif action == "update":
        rate.set_existing_stats()
