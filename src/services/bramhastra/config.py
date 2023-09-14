class LifeCycleConfig:
    def __init__(self) -> None:
        flow = {
            "name": "Spot Search",
            "rates_count": None,
            "parent": "GLOBAL PARENT",
            "child": {
                "right": [
                    {
                        "name": "Checkout",
                        "rates_count": None,
                        "drop": None,
                        "child": {
                            "right": [
                                {
                                    "name": "Shipment",
                                    "rates_count": None,
                                    "drop": None,
                                    "child": {
                                        "bottom": [
                                            {
                                                "name": "Revenue Desk",
                                                "rates_count": None,
                                                "drop": None,
                                                "child": {
                                                    "bottom": [
                                                        {
                                                            "name": "SO1",
                                                            "rates_count": None,
                                                            "child": {},
                                                            "drop": None,
                                                        }
                                                    ]
                                                },
                                            }
                                        ],
                                        "right": [
                                            {
                                                "name": "Received",
                                                "rates_count": None,
                                                "drop": None,
                                                "child": {
                                                    "right": [
                                                        {
                                                            "name": "Confirmed",
                                                            "rates_count": None,
                                                            "drop": None,
                                                            "child": {
                                                                "right": [
                                                                    {
                                                                        "name": "Cancelled",
                                                                        "rates_count": None,
                                                                        "drop": None,
                                                                        "child": {},
                                                                    },
                                                                    {
                                                                        "name": "Aborted",
                                                                        "rates_count": None,
                                                                        "drop": None,
                                                                        "child": {},
                                                                    },
                                                                    {
                                                                        "name": "Completed",
                                                                        "rates_count": None,
                                                                        "drop": None,
                                                                        "child": {},
                                                                    },
                                                                ],
                                                            },
                                                        },
                                                    ],
                                                    "top": [
                                                        {
                                                            "name": "OUTDATED",
                                                            "rates_count": None,
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
