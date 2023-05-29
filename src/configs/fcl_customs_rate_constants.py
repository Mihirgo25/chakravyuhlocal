from global_constants import HAZ_CLASSES, STANDARD_COMMODITIES

REQUEST_SOURCES = ['spot_search']

FEEDBACK_SOURCES = ['spot_search', 'checkout']

FEEDBACK_TYPES = ['liked', 'disliked']

CONTAINER_TYPE_COMMODITY_MAPPINGS = {
    'standard' : [None] + HAZ_CLASSES + STANDARD_COMMODITIES,
    'refer' : [None],
    'open_top' : [None],
    'open_side' : [None],
    'flat_rack' : [None],
    'iso_tank' : [None] + HAZ_CLASSES
}

LOCATION_HIERARCHY = {
    'seaport' : 1,
    'country' : 2
}