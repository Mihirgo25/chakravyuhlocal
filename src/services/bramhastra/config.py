class LifeCycleConfig:
    def __init__(self, spot_search_count, input) -> None:
        self.spot_search_count = spot_search_count
        self.input = input

    def get_flow(self) -> dict:
        return {
            "name": "spot_search",
            "count": self.spot_search_count,
            "parent": "global_parent",
            "child": {
                "right": [
                    {
                        "name": "checkout",
                        "count": self.input.get("checkout_count"),
                        "drop": self.input.get("checkout_dropoff"),
                        "child": {
                            "right": [
                                {
                                    "name": "shipment",
                                    "count": None,
                                    "drop": None,
                                    "child": {
                                        "right": [
                                            {
                                                "name": "confirmed",
                                                "count": None,
                                                "drop": None,
                                                "child": {
                                                    "right": [
                                                        {
                                                            "name": "completed",
                                                            "count": None,
                                                            "drop": None,
                                                            "child": {},
                                                        },
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "aborted",
                                                "count": None,
                                                "drop": None,
                                                "child": {
                                                    "right": [
                                                        {
                                                            "name": "completed",
                                                            "count": None,
                                                            "drop": None,
                                                            "child": {},
                                                        },
                                                    ],
                                                },
                                            },
                                            {
                                                "name": "cancelled",
                                                "count": None,
                                                "drop": None,
                                                "child": {
                                                    "bottom": [
                                                        {
                                                            "name": "completed",
                                                            "count": None,
                                                            "drop": None,
                                                            "child": {},
                                                        },
                                                    ],
                                                },
                                            },
                                        ],
                                        "bottom": [
                                            {
                                                "name": "revenue_desk",
                                                "count": None,
                                                "drop": None,
                                                "child": {
                                                    "bottom": [
                                                        {
                                                            "name": "so1",
                                                            "count": None,
                                                            "drop": None,
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
        }

    def get_dislike_flow(self) -> dict:
        return {
            "name": "spot_search",
            "count": self.spot_search_count,
            "drop": None,
            "parent": "global_parent",
            "child": {
                "right": [
                    {
                        "name": "rates_shown",
                        "count": None,
                        "drop": None,
                        "child": {
                            "right": [
                                {
                                    "name": "disliked",
                                    "count": None,
                                    "drop": None,
                                    "child": {
                                        "right": [
                                            {
                                                "name": "feedback_received",
                                                "count": None,
                                                "drop": None,
                                                "child": {
                                                    "right": [
                                                        {
                                                            "name": "rate_reverted_feedbacks",
                                                            "count": None,
                                                            "drop": None,
                                                            "child": {
                                                                "right": [
                                                                    {
                                                                        "name": "rates_reverted",
                                                                        "count": None,
                                                                        "drop": None,
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
                                {
                                    "name": "liked",
                                    "count": None,
                                    "drop": None,
                                    "child": {},
                                },
                            ],
                        },
                    },
                ],
            },
        }

    def get_rate_request_flow(self) -> dict:
        return {
            "name": "spot_search",
            "count": self.spot_search_count,
            "drop": None,
            "parent": "global_parent",
            "child": {
                "right": [
                    {
                        "name": "rates_requested",
                        "count": input.get("rates_requested_count"),
                        "drop": input.get("rates_requested_percentage"),
                        "parent": "global_parent",
                        "child": {
                            "right": [
                                {
                                    "name": "requests_closed",
                                    "count": input.get("requests_closed"),
                                    "drop": None,
                                    "parent": "global_parent",
                                    "child": {
                                        "right": [
                                            {
                                                "name": "rates_reverted",
                                                "count": input.get("rates_reverted"),
                                                "drop": None,
                                                "parent": "global_parent",
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
        }
