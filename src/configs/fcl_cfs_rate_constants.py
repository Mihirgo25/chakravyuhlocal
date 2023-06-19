from configs.global_constants import HAZ_CLASSES,STANDARD_COMMODITIES
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

EXPORT_CARGO_HANDLING_TYPES = ['stuffing_at_factory', 'stuffing_at_dock']

IMPORT_CARGO_HANDLING_TYPES = ['direct_port_delivery', 'delivery_from_dock', 'destuffing_at_dock', 'dpd_without_cfs', 'dpd_cfs_dock_destuffing', 'dpd_cfs_factory_destuffing', 'enpanelled_cfs_dock_destuffing', 'enpanelled_cfs_factory_destuffing', 'non_enpanelled_cfs_dock_destuffing', 'non_enpanelled_cfs_factory_destuffing']