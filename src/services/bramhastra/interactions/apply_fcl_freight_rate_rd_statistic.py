from services.bramhastra.helpers.rd_fcl_freight_rate_statistic_helper import RevenueDesk
from services.bramhastra.enums import RDAction, AppEnv
from configs.env import APP_ENV


def apply_fcl_freight_rate_rd_statistic(request):
    if APP_ENV == AppEnv.production.value:
        revenue_desk = RevenueDesk(request)
        if (
            not getattr(request, "selected_for_booking")
            and request.action == RDAction.create.value
        ):
            revenue_desk.update_rd_visit_count(request)
            return

        if request.action == RDAction.update.value and getattr(
            request, "selected_for_booking"
        ):
            revenue_desk.set(request)
        elif request.action == RDAction.update.value and getattr(
            request, "selected_for_preference"
        ):
            revenue_desk.update_selected_for_preference_count(request)
