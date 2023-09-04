from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from services.bramhastra.helpers.common_statistic_helper import get_identifier
from micro_services.client import common
from services.bramhastra.enums import FeedbackAction
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)


class Feedback:
    def __init__(self, action, params) -> None:
        self.increment_keys = set()
        self.decrement_keys = set()

        self.params = params.dict(exclude={"likes_count", "dislikes_count"})

        self.rate_stats_update_params = dict()

        if getattr(params, "likes_count") == 1:
            self.increment_keys.add("likes_count")
        elif getattr(params, "dislikes_count") == 1:
            self.increment_keys.add("dislikes_count")

        self.rate_id = params.rate_id
        self.validity_id = params.validity_id

        if action == FeedbackAction.update.value:
            if getattr(params, "likes_count") == -1:
                self.decrement_keys.add("likes_count")
            elif getattr(params, "dislikes_count") == -1:
                self.decrement_keys.add("dislikes_count")

        self.exclude_update_params = {"feedback_id"}

        self.feedback_id = params.feedback_id

        if self.params.get("currency") and self.params.get("currency") != "USD":
            self.rate_stats_update_params[
                "last_indicative_rate"
            ] = common.get_money_exchange_for_fcl(
                {
                    "price": self.params.get("preferred_freight_rate"),
                    "from_currency": self.params.get("currency"),
                    "to_currency": "USD",
                }
            )[
                "price"
            ]
        self.rate_stats_update_params["last_indicative_rate"] = (
            self.params.get("preferred_freight_rate") or 0
        )

    def set_format_and_existing_rate_stats(self):
        if (
            not self.increment_keys
            and not self.decrement_keys
            and not self.rate_stats_update_params
        ):
            return

        fcl_freight_rate_statistic = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier
                == get_identifier(self.rate_id, self.validity_id)
            )
            .first()
        )

        if fcl_freight_rate_statistic:
            self.params["fcl_freight_rate_statistic_id"] = fcl_freight_rate_statistic.id

            for key in self.increment_keys:
                setattr(
                    fcl_freight_rate_statistic,
                    key,
                    getattr(fcl_freight_rate_statistic, key) + 1,
                )
            for key in self.decrement_keys:
                setattr(
                    fcl_freight_rate_statistic,
                    key,
                    max(getattr(fcl_freight_rate_statistic, key) - 1, 0),
                )
            for key, value in self.rate_stats_update_params.items():
                if value:
                    setattr(fcl_freight_rate_statistic, key, value)

            fcl_freight_rate_statistic.save()

    def set_new_stats(self) -> int:
        return FeedbackFclFreightRateStatistic.insert_many(self.params).execute()

    def set_existing_stats(self) -> None:
        feedback = (
            FeedbackFclFreightRateStatistic.select()
            .where(
                FeedbackFclFreightRateStatistic.feedback_id
                == self.params.get("feedback_id")
            )
            .first()
        )

        if feedback:
            for key in self.params.keys():
                if key not in self.exclude_update_params:
                    if self.params.get(key):
                        setattr(feedback, key, self.params.get(key))
            try:
                feedback.save()
            except Exception as e:
                raise e
