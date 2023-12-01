from services.bramhastra.models.feedback_air_freight_rate_statistic import (
    FeedbackAirFreightRateStatistic,
)
from services.bramhastra.helpers.common_statistic_helper import (
    get_air_freight_identifier,
    create_air_freight_rate_statistic_fallback,
)
from micro_services.client import common
from services.bramhastra.enums import (
    FeedbackAction,
    AirFeedbackClosingRemarks,
    AirFeedbackStatus,
)
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.models.air_freight_action import AirFreightAction
from services.bramhastra.enums import FeedbackState, FeedbackType
import uuid


class Feedback:
    def __init__(self, action, params) -> None:
        self.increment_keys = set()
        self.decrement_keys = set()
        self.action = action
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
            ] = common.get_money_exchange_for_Air(
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

    def update_foreign_references(self):
        self.__update_air_freight_statistic()
        self.__update_air_freight_action()

    def __update_air_freight_statistic(self):
        if not any(
            [self.increment_keys, self.decrement_keys, self.rate_stats_update_params]
        ):
            return

        air_freight_rate_statistic = (
            AirFreightRateStatistic.select()
            .where(
                AirFreightRateStatistic.identifier
                == get_air_freight_identifier(self.rate_id, self.validity_id)
            )
            .first()
        ) or create_air_freight_rate_statistic_fallback(self.rate_id, self.validity_id)

        if air_freight_rate_statistic is not None:
            self.params["air_freight_rate_statistic_id"] = air_freight_rate_statistic.id

            for key in self.increment_keys:
                setattr(
                    air_freight_rate_statistic,
                    key,
                    getattr(air_freight_rate_statistic, key) + 1,
                )
            for key in self.decrement_keys:
                setattr(
                    air_freight_rate_statistic,
                    key,
                    max(getattr(air_freight_rate_statistic, key) - 1, 0),
                )
            for key, value in self.rate_stats_update_params.items():
                if value:
                    setattr(air_freight_rate_statistic, key, value)

            air_freight_rate_statistic.save()

    def __update_air_freight_action(self):
        air_freight_action = self.__get_air_freight_action()
        if air_freight_action is None:
            return
        if self.action == FeedbackAction.create.value:
            setattr(
                air_freight_action,
                AirFreightAction.feedback_state.name,
                FeedbackState.created.name,
            )
            feedback_ids = getattr(
                air_freight_action, AirFreightAction.feedback_ids.name
            )
            if not feedback_ids:
                feedback_ids = [
                    self.params.get(FeedbackAirFreightRateStatistic.feedback_id.name)
                ]
            else:
                feedback_ids.append(
                    self.params.get(FeedbackAirFreightRateStatistic.feedback_id.name)
                )
            feedback_ids = [
                uuid.UUID(uuid_str) if isinstance(uuid_str, str) else uuid_str
                for uuid_str in feedback_ids
            ]
            setattr(
                air_freight_action,
                AirFreightAction.feedback_ids.name,
                feedback_ids,
            )
            setattr(
                air_freight_action,
                AirFreightAction.feedback_type.name,
                (
                    FeedbackType.liked.name
                    if "likes_count" in self.increment_keys
                    else FeedbackType.disliked.name
                ),
            )
        else:
            if (
                self.params.get(FeedbackAirFreightRateStatistic.status.name)
                == AirFeedbackStatus.inactive.name
            ):
                setattr(
                    air_freight_action,
                    AirFreightAction.feedback_state.name,
                    FeedbackState.closed.name,
                )
            if (
                self.params.get(FeedbackAirFreightRateStatistic.is_rate_reverted.name)
                is True
            ):
                setattr(
                    air_freight_action,
                    AirFreightAction.feedback_state.name,
                    FeedbackState.rate_added.name,
                )

        setattr(
            air_freight_action,
            AirFreightAction.updated_at.name,
            self.params.get(FeedbackAirFreightRateStatistic.updated_at.name),
        )
        air_freight_action.save()

    def __get_air_freight_action(self):
        return (
            AirFreightAction.select()
            .where(
                AirFreightAction.spot_search_id == self.params.get("source_id"),
                AirFreightAction.rate_id == self.params.get("rate_id"),
                AirFreightAction.validity_id == self.params.get("validity_id"),
            )
            .first()
        )

    def create(self) -> int:
        return FeedbackAirFreightRateStatistic.insert_many(self.params).execute()

    def update(self) -> None:
        feedback = (
            FeedbackAirFreightRateStatistic.select()
            .where(
                FeedbackAirFreightRateStatistic.feedback_id
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
