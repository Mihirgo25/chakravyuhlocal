from database.db_session import db
from services.bramhastra.helpers.post_fcl_freight_helper import Request
from services.bramhastra.enums import RequestAction


def apply_fcl_freight_rate_request_statistic(request):
    with db.atomic():
        execute_transaction_code(request)


def execute_transaction_code(request):
    feedback = Request(params=request.params)
    if request.action == RequestAction.create.value:
        feedback.set_new_stats()
    elif request.action == RequestAction.delete.value:
        feedback.set_existing_stats()
