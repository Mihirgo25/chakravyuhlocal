from database.db_session import db
from services.bramhastra.helpers.request_fcl_freight_rate_helper import Request
from services.bramhastra.enums import RequestAction
from configs.env import APP_ENV


def apply_fcl_freight_rate_request_statistic(request):
    if APP_ENV == "production":
        feedback = Request(params=request.params)
        if request.action == RequestAction.create.value:
            feedback.set_new_stats()
        elif request.action == RequestAction.delete.value:
            feedback.set_existing_stats()
