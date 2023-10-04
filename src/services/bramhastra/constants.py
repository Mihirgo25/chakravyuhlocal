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

DEFAULT_ENUM = "empty"

UNIQUE_FCL_SPOT_SEARCH_SERVICE_KEYS = {"commodity", "container_size", "container_type"}

GLOBAL_MIN = -1000000000000000  # 10e-15

DIFFERENCE_CHOICE_TYPE = ["rate_request", "feedback"]

AGGREGATE_FILTER_MAPPING = {
    "average_standard_price": {
        "state": "",
        "value": "",
        "method": "(SUM(standard_price*sign)/COUNT(DISTINCT checkout_id))",
    },
    "liked": {
        "state": "feedback_type",
        "value": "'liked'",
        "method": "COUNT(DISTINCT id)",
    },
    "disliked": {
        "state": "feedback_type",
        "value": "'disliked'",
        "method": "COUNT(DISTINCT id)",
    },
    "bas_standard_price_accuracy": {
        "state": "",
        "value": "",
        "method": "(SUM(bas_standard_price_accuracy*sign)/COUNT(DISTINCT checkout_id))",
    },
    "spot_search": {
        "state": "",
        "value": "",
        "method": "COUNT(DISTINCT spot_search_id)",
    },
    "checkout": {
        "state": "checkout",
        "value": "0",
        "comparator": ">",
        "method": "COUNT(DISTINCT checkout_id)",
    },
    "shipment_completed": {
        "state": "shipment_state",
        "value": "'completed'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "shipment_cancelled": {
        "state": "shipment_state",
        "value": "'cancelled'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "shipment_aborted": {
        "state": "shipment_state",
        "value": "'aborted'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "shipment_confirmed_by_importer_exporter": {
        "state": "shipment_state",
        "value": "'confirmed_by_importer_exporter'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "shipment_in_progress": {
        "state": "shipment_state",
        "value": "'in_progress'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "shipment_received": {
        "state": "shipment_state",
        "value": "'received'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "revenue_desk_visit": {
        "state": "revenue_desk_state",
        "value": "'visited'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "so1_visit": {
        "state": "revenue_desk_state",
        "value": "'selected_for_preference'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "so1_select": {
        "state": "revenue_desk_state",
        "value": "'selected_for_booking'",
        "method": "COUNT(DISTINCT shipment_id)",
    },
    "rate_requests_created": {
        "state": "rate_request_state",
        "value": "'created'",
        "method": "COUNT(DISTINCT id)",
    },
    "rate_requests_reverted": {
        "state": "rate_request_state",
        "value": "'rate_added'",
        "method": "COUNT(DISTINCT id)",
    },
}
