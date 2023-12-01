from database.db_session import db
from services.bramhastra.helpers.feedback_air_freight_rate_statistic_helper import (
    Feedback,
)
from services.bramhastra.enums import FeedbackAction
from configs.env import APP_ENV
from services.bramhastra.enums import AppEnv
from services.bramhastra.models.feedback_air_freight_rate_statistic import (
    FeedbackAirFreightRateStatistic,
)


def apply_feedback_air_freight_rate_statistic(request):
    if APP_ENV == AppEnv.production.value:
        with FeedbackAirFreightRateStatistic._meta.database.atomic():
            feedback = Feedback(action=request.action, params=request.params)
            feedback.update_foreign_references()
            if request.action == FeedbackAction.create.value:
                feedback.create()
            elif (
                request.action == FeedbackAction.update.value
                or request.action == FeedbackAction.delete.value
            ):
                feedback.update()