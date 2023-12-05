from services.bramhastra.helpers.air_freight_rate_statistic_helper import Rate
from configs.env import APP_ENV
from services.bramhastra.enums import AppEnv
from enums.global_enums import Action


def apply_air_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        setting_air_freight_rate_statistic(request.action, request.params)


def setting_air_freight_rate_statistic(action, params):
    rate = Rate(freight=params.freight)
    rate.set_pricing_map_zone_ids()
    if action == Action.delete:
        rate.delete_latest_stat()
        return
    rate.set_formatted_data()
    if action == Action.create:
        rate.set_new_stats()
    elif action == Action.update:
        rate.set_existing_stats()
