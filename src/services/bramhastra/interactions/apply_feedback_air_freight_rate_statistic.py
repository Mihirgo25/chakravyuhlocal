from database.db_session import db
from services.bramhastra.helpers.post_air_freight_helper import Feedback
from services.bramhastra.enums import FeedbackAction


def apply_feedback_air_freight_rate_statistic(request):
    with db.atomic():
        execute_transaction_code(request)


def execute_transaction_code(request):
    feedback = Feedback(request.params)
    feedback.set_format_and_existing_rate_stats()
    if request.action == FeedbackAction.create.value:
        feedback.set_new_stats()
    elif request.action == FeedbackAction.update.value:
        feedback.set_existing_stats()
