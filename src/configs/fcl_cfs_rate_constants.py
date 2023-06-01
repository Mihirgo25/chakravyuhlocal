from global_constants import TRADE_TYPES,HAZ_CLASSES,STANDARD_COMMODITIES
REQUEST_SOURCES = ['spot_search']

TRADE_TYPES =  ['import', 'export', 'domestic']


CONTAINER_TYPE_COMMODITY_MAPPINGS = {
        'standard': [None] + HAZ_CLASSES + STANDARD_COMMODITIES,
        'refer': [None],
        'open_top': [None],
        'open_side': [None],
        'flat_rack': [None],
        'iso_tank': [None] +HAZ_CLASSES
    }

LOCATION_HIERARCHY = {
        'seaport': 1,
        'country': 2
    }

FREE_DAYS_TYPES = [
        {
            'name': "Ground Rent Free Days",
            'type': "ground_rent",
            'tags': ["mandatory"]
        },
        {
            'name': "Refer Plugin Free Days",
            'type': "refer_plugin",
            'tags': []
        }
        ]