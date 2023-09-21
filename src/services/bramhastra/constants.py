INDIAN_LOCATION_ID = "541d1232-58ce-4d64-83d6-556a42209eb7"
DEFAULT_START_DATE = "2016-03-01"
ALL_TIME_ACCURACY_JSON_FILE_PATH = "./all_time_accuracy.json"
BRAHMASTRA_CSV_FILE_PATH = "./brahmastra.csv"

STANDARD_WEIGHT_SLABS = [
    {
        "lower_limit": 0.0,
        "upper_limit": 45,
        "tariff_price": 0,
        "currency": "INR",
        "unit": "per_kg",
    },
    {
        "lower_limit": 45.1,
        "upper_limit": 100.0,
        "currency": "INR",
        "tariff_price": 0,
        "unit": "per_kg",
    },
    {
        "lower_limit": 100.1,
        "upper_limit": 300.0,
        "currency": "INR",
        "tariff_price": 0,
        "unit": "per_kg",
    },
    {
        "lower_limit": 300.1,
        "upper_limit": 500.0,
        "currency": "INR",
        "tariff_price": 0,
        "unit": "per_kg",
    },
    {
        "lower_limit": 500.1,
        "upper_limit": 1000.0,
        "currency": "INR",
        "tariff_price": 0,
        "unit": "per_kg",
    },
    {
        "lower_limit": 1000.1,
        "upper_limit": 10000,
        "currency": "INR",
        "tariff_price": 0,
        "unit": "per_kg",
    },
]

DEFAULT_RATE_TYPE = "market_place"


FCL_MODE_MAPPINGS = {
    "rate_extension": "rate_extension",
    "manual": "supply",
    "rate_sheet": "supply",
    "predicted": "predicted",
    "cluster_extension": "cluster_extension",
    "disliked_rate": "supply",
    "flash_booking": "supply",
    "rms_upload": "supply",
    "missing_rate": "supply",
    "spot_negotation": "supply",
    "cogolens": "predicted",
}

SHIPMENT_RATE_STATS_KEYS = [
    "rate_deviation_from_latest_booking",
    "average_booking_rate",
    "rate_deviation_from_booking_rate",
    "accuracy",
]

DEFAULT_UUID = "00000000-0000-0000-0000-000000000000"

UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS = {"commodity","container_size","container_type"}

GLOBAL_MIN = -1000000000000000  # 10e-15