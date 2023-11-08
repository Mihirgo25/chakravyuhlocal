from configs.global_constants import HAZ_CLASSES, STANDARD_COMMODITIES

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

FCL_CUSTOMS_COVERAGE_USERS = [
    '6addea60-a3de-4067-b08d-ece04be594ab',
    'f47788fe-85e8-4f86-a9d7-7c7902ea864a',
    '51641e0e-a5da-452a-81fc-ccb8fe6df343',
    'd7f62f2d-2b41-41ae-a9f0-200255de4d8f',
    '922b367f-0f3e-4872-91d0-68413fc7f955',
    '329fb317-f2f9-4c41-aabd-4a9befc53721'
]

EXPORT_CARGO_HANDLING_TYPES = ['stuffing_at_factory', 'stuffing_at_dock']

IMPORT_CARGO_HANDLING_TYPES = [
    'direct_port_delivery', 
    'delivery_from_dock', 
    'destuffing_at_dock', 
    'dpd_without_cfs', 
    'dpd_cfs_dock_destuffing', 
    'dpd_cfs_factory_destuffing', 
    'enpanelled_cfs_dock_destuffing', 
    'enpanelled_cfs_factory_destuffing', 
    'non_enpanelled_cfs_dock_destuffing', 
    'non_enpanelled_cfs_factory_destuffing'
    ]