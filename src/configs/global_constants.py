HAZ_CLASSES = [
    "gases-2.1",
    "gases-2.2",
    "gases-2.3",
    "flammable_liquids-3",
    "flammable_solids-4.1",
    "flammable_solids_self_heat-4.2",
    "emit_flammable_gases_with_water-4.3",
    "imo_classes-5.1",
    "toxic_substances-6.1",
    "infectious_substances-6.2",
    "radioactive_material-7",
    "corrosives-8",
    "miscellaneous_dangerous_goods-9"
  ]

SEARCH_START_DATE_OFFSET = 2

DEFAULT_EXPORT_DESTINATION_DETENTION = 7

DEFAULT_IMPORT_DESTINATION_DETENTION = 4

MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT = 100000

CONFIRMED_INVENTORY = {
    'service_provider_ids': ["536abfe7-eab8-4a43-a4c3-6ff318ce01b5"], #CogoXpress
    'tag': "confirmed_inventory"
}

PREDICTED_RATES_SERVICE_PROVIDER_IDS = ["6cc6b696-60f6-480b-bcbe-92cc8e642531"]

DEFAULT_PAYMENT_TERM = 'prepaid'

INTERNAL_BOOKING = {
    'service_provider_id': "5dc403b3-c1bd-4871-b8bd-35543aaadb36"
}

DEFAULT_SPECIFICITY_TYPE = 'shipping_line'