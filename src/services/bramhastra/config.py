class LifeCycleConfig:
    def __init__(self, input) -> None:
        self.input = input

    def fill_flows(self) -> dict:
        response = {}

        response["business_flow"] = {
            "name": "spot_search",
            "count": self.input.get("spot_search"),
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
                                    "count": self.input.get("shipment_count"),
                                    "drop": self.input.get("shipment_dropoff"),
                                    "child": {
                                        "right": [
                                            {
                                                "name": "confirmed",
                                                "count": self.input.get("confirmed_count"),
                                                "drop": self.input.get("confirmed_dropoff"),
                                                "child": {
                                                    "right": [
                                                        {
                                                            "name": "completed",
                                                            "count": self.input.get("completed_count"),
                                                            "drop": self.input.get("completed_dropoff"),
                                                            "child": {},
                                                        },
                                                        {
                                                            "name": "aborted",
                                                            "count": self.input.get("aborted_count"),
                                                            "drop": self.input.get("aborted_dropoff"),
                                                            "child": {},
                                                        },
                                                        
                                                        {
                                                            "name": "cancelled",
                                                            "count": self.input.get("cancelled_count"),
                                                            "drop": self.input.get("cancelled_dropoff"),
                                                            "child": {},
                                                        },
                                                    ],
                                                },
                                            },
                                            
                                        ],
                                        "bottom": [
                                            {
                                                "name": "revenue_desk",
                                                "count": self.input.get("revenue_desk_count"),
                                                "drop": self.input.get("revenue_desk_dropoff"),
                                                "child": {
                                                    "bottom": [
                                                        {
                                                            "name": "so1",
                                                            "count": self.input.get("so1_count"),
                                                            "drop": self.input.get("so1_dropoff"),
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

        response["dislike_flow"] = {
            "name": "spot_search",
            "count": self.input.get("spot_search"),
            "parent": "global_parent",
            "child": {
                "right": [
                    {
                        "name": "rates_shown",
                        "count": self.input.get("rates_shown_count"),
                        "drop": self.input.get("rates_shown_dropoff"),
                        "child": {
                            "right": [
                                {
                                    "name": "disliked",
                                    "count": self.input.get("disliked_count"),
                                    "drop": self.input.get("disliked_dropoff"),
                                    "child": {
                                        "right": [
                                            {
                                                "name": "feedback_received",
                                                "count": self.input.get("feedback_received_count"),
                                                "drop": self.input.get("feedback_received_dropoff"),
                                                "child": {
                                                    "right": [
                                                        {
                                                            "name": "rate_reverted_feedbacks",
                                                            "count": self.input.get("rate_reverted_feedbacks_count"),
                                                            "drop": self.input.get("rate_reverted_feedbacks_dropoff"),
                                                            "child": {
                                                                "right": [
                                                                    {
                                                                        "name": "feedback_rates_added",
                                                                        "count": self.input.get("feedback_rates_added_count"),
                                                                        "drop": self.input.get("feedback_rates_added_dropoff"),
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
                                    "count": self.input.get("liked_count"),
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
            "count": self.input.get("spot_search"),
            "parent": "global_parent",
            "child": {
                "right": [
                    {
                        "name": "rates_requested",
                        "count": input.get("rates_requested_count"),
                        "drop": input.get("rates_requested_dropoff"),
                        "parent": "global_parent",
                        "child": {
                            "right": [
                                {
                                    "name": "requests_closed",
                                    "count": input.get("requests_closed_count"),
                                    "drop": input.get("requests_closed_dropoff"),
                                    "parent": "global_parent",
                                    "child": {
                                        "right": [
                                            {
                                                "name": "rates_reverted",
                                                "count": input.get("rates_reverted_count"),
                                                "drop": input.get("rates_reverted_dropoff"),
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

        return response
