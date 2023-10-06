from database.db_session import db
from services.bramhastra.helpers.feedback_fcl_freight_rate_helper import Feedback
from services.bramhastra.enums import FeedbackAction
from configs.env import APP_ENV


def apply_feedback_fcl_freight_rate_statistic(request):
    with db.atomic():
        execute_transaction_code(request)


def execute_transaction_code(request):
    if APP_ENV == "production":
        feedback = Feedback(action=request.action, params=request.params)
        feedback.set_format_and_existing_rate_stats()
        if request.action == FeedbackAction.create.value:
            feedback.set_new_stats()
        elif (
            request.action == FeedbackAction.update.value
            or request.action == FeedbackAction.delete.value
        ):
            feedback.set_existing_stats()
