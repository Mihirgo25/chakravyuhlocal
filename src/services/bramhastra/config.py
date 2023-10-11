class LifeCycleConfig:
    def __init__(self, input) -> None:
        self.input = input

    def fill_flows(self) -> dict:
        response = {}

        response["business_flow"] = {
            "name": "spot_search",
            "rates_count": self.input.get("spot_search_count"),
            "parent": "global_parent",
            "child": {
                "right": [
                    {
                        "name": "checkout",
                        "rates_count": self.input.get("checkout_count"),
                        "drop": self.input.get("checkout_dropoff"),
                        "child": {
                            "right": [
                                {
                                    "name": "shipment_received",
                                    "rates_count": self.input.get("shipments_received"),
                                    "drop": self.input.get("shipment_dropoff"),
                                    "child": {
                                        "right": [
                                            {
                                                "name": "confirmed",
                                                "rates_count": self.input.get(
                                                    "confirmed_count"
                                                ),
                                                "drop": self.input.get(
                                                    "confirmed_dropoff"
                                                ),
                                                "child": {
                                                    "right": [
                                                        {
                                                            "name": "completed",
                                                            "rates_count": self.input.get(
                                                                "completed_count"
                                                            ),
                                                            "drop": self.input.get(
                                                                "completed_dropoff"
                                                            ),
                                                            "child": {},
                                                        },
                                                        {
                                                            "name": "aborted",
                                                            "rates_count": self.input.get(
                                                                "aborted_count"
                                                            ),
                                                            "drop": self.input.get(
                                                                "aborted_dropoff"
                                                            ),
                                                            "child": {},
                                                        },
                                                        {
                                                            "name": "cancelled",
                                                            "rates_count": self.input.get(
                                                                "cancelled_count"
                                                            ),
                                                            "drop": self.input.get(
                                                                "cancelled_dropoff"
                                                            ),
                                                            "child": {},
                                                        },
                                                    ],
                                                    "bottom": [
                                                        {
                                                            "name": "revenue_desk",
                                                            "rates_count": self.input.get(
                                                                "revenue_desk_count"
                                                            ),
                                                            "drop": self.input.get(
                                                                "revenue_desk_dropoff"
                                                            ),
                                                            "child": {
                                                                "bottom": [
                                                                    {
                                                                        "name": "so1",
                                                                        "rates_count": self.input.get(
                                                                            "so1_count"
                                                                        ),
                                                                        "drop": self.input.get(
                                                                            "so1_dropoff"
                                                                        ),
                                                                        "child": {},
                                                                    },
                                                                ],
                                                            },
                                                        },
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                },
                            ],
                        },
                    },
                ],
            },
        }

        response["dislike_flow"] = {
            "name": "spot_search",
            "rates_count": self.input.get("spot_search_count"),
            "parent": "global_parent",
            "child": {
                "right": [
                    {
                        "name": "feedbacks_created",
                        "rates_count": self.input.get("feedbacks_created_count"),
                        "drop": self.input.get("feedbacks_created_dropoff"),
                        "child": {
                            "right": [
                                {
                                    "name": "disliked",
                                    "rates_count": self.input.get("disliked_count"),
                                    "drop": self.input.get("disliked_dropoff"),
                                    "child": {
                                        "right": [
                                            {
                                                "name": "feedback_closed",
                                                "rates_count": self.input.get(
                                                    "feedback_closed_count"
                                                ),
                                                "drop": self.input.get(
                                                    "feedback_closed_dropoff"
                                                ),
                                                "child": {
                                                    "right": [
                                                        {
                                                            "name": "feedbacks_reverted",
                                                            "rates_count": self.input.get(
                                                                "feedbacks_with_rate_added"
                                                            ),
                                                            "drop": self.input.get(
                                                                "feedbacks_with_rate_added_dropoff"
                                                            ),
                                                            "child": {},
                                                        },
                                                    ],
                                                },
                                            },
                                        ],
                                    },
                                },
                                {
                                    "name": "liked",
                                    "rates_count": self.input.get("liked_count"),
                                    "drop": self.input.get("liked_dropoff"),
                                    "child": {},
                                },
                            ],
                        },
                    },
                ],
            },
        }

        response["rate_request_flow"] = {
            "name": "spot_search",
            "rates_count": self.input.get("spot_search_count"),
            "parent": "global_parent",
            "child": {
                "right": [
                    {
                        "name": "rates_requested",
                        "rates_count": self.input.get("rates_requested_count"),
                        "drop": self.input.get("rates_requested_dropoff"),
                        "child": {
                            "right": [
                                {
                                    "name": "requests_closed",
                                    "rates_count": self.input.get(
                                        "requests_closed_count"
                                    ),
                                    "drop": self.input.get("requests_closed_dropoff"),
                                    "child": {},
                                },
                            ],
                        },
                    },
                ],
            },
        }

        return response
