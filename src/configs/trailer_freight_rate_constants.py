DEFAULT_MAX_WEIGHT_LIMIT = {
    '20': 18,
    '40': 30,
    '40HC':32.5,
    '45HC': 32.68
}

CONTAINER_SIZES = ['20', '40', '40HC', '45HC']

CONTAINER_TYPES = ['standard', 'refer', 'open_top', 'open_side', 'flat_rack', 'iso_tank']

CALCULATION_COUNTRY_CODES = ['IN', 'CN', 'US']

DEFAULT_CALCULATION_COUNTRY_CODE = "US"

CALCULATION_CURRENCY_CODES = ['INR', 'CNY','USD', 'VND']

DEFAULT_FUEL_PRICES = {
    "INR": 107,
    "USD": 1.1,
    "CNY": 9.07
}

DEFAULT_SERVICE_PROVIDER_ID = '5dc403b3-c1bd-4871-b8bd-35543aaadb36'

CONTAINER_SIZE_FACTORS = {
    '20': 1,
    '40': 1.4,
    '40HC': 1.8,
    '45HC': 2
}

CONTAINR_TYPE_FACTORS = {
    'standard': 1,
    'refer': 1.6,
    'open_top': 1.4,
    'flat_rack': 1.3,
    'open_side': 1.4, 
    'iso_tank': 1.5
}