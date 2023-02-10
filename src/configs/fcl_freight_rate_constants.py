HAZ_COMMODITIES = [
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

CONTAINER_SIZES = ['20', '40', '40HC', '45HC']

CONTAINER_TYPES = ['standard', 'refer', 'open_top', 'open_side', 'flat_rack', 'iso_tank']

FAK_COMMODITY = ["general"]

STANDARD_COMMODITIES = ['white_goods', 'pta', 'agro', 'cotton_and_yarn', 'fabric_and_textiles', 'raw_cotton', 'rice_bran', 'sugar_rice']

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

REFER_COMMODITIES = ['chilled', 'frozen', 'pharma', 'meat', 'sea_food', 'fruits_and_veg']

OPEN_TOP_COMMODITIES = ['in_gauge_cargo']

OPEN_SIDE_COMMODITIES = []

FLAT_RACK_COMMODITIES = ['in_gauge_cargo']

ISO_TANK_COMMODITIES = ['non_haz_solids', 'non_haz_liquids', 'non_haz_gases']

FREIGHT_CONTAINER_COMMODITY_MAPPINGS = {
    'standard' : FAK_COMMODITY + STANDARD_COMMODITIES + HAZ_CLASSES,
    'refer' : REFER_COMMODITIES,
    'open_top' : OPEN_TOP_COMMODITIES,
    'open_side' : FAK_COMMODITY + OPEN_SIDE_COMMODITIES,
    'flat_rack' : FLAT_RACK_COMMODITIES,
    'iso_tank' : ISO_TANK_COMMODITIES + HAZ_CLASSES
  }

TRADE_TYPES = ['import', 'export', 'domestic']

LOCAL_CONTAINER_COMMODITY_MAPPINGS = {
    'standard': [None] + HAZ_COMMODITIES,
    'refer': [None],
    'open_top': [None],
    'open_side': [None],
    'flat_rack': [None],
    'iso_tank': [None] + HAZ_COMMODITIES
  }