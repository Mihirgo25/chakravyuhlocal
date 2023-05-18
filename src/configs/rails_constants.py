DEFAULT_PERMISSIBLE_CARRYING_CAPACITY = 54.90

DESTINATION_TERMINAL_CHARGES_INDIA = 15

CONTAINER_TYPE_CLASS_MAPPINGS = {
    # 120 refer
    'standard' : ['Class 120'],
    'refer' : ['Class 130A', 'Class 200'],
    'open_top' : ['Class 140A'],
    'open_side' : ['Class 170'],
    'flat_rack' : ['Class 180A'],
    'iso_tank' : ['Class 150'],
 }

WAGON_CONTAINER_TYPE_MAPPINGS = {
    'standard' : ['BCX', 'BCXC', 'BCXR', 'BCXT', 'BCXN', 'BCN', 'BCNA', 'BCNAHS', 'BCNHL', 'BCNAHS'],
    'refer' : [],
    'open_top': ['BOXNHL','BOXNHS', 'BOXNS', 'BOY'],
    'open_side' : ['BOBYN', 'BOBSN', 'BCFC', 'BOBRN'],
    'flat_rack' : ['BRNA','BRNA-EUR','BFNS','BFNSM1','BFNSM'],
    'iso_tank' : ['BTNP', 'BTAP', 'BTALN', 'BTPGLN', 'BTCS'],
}

WAGON_MAPPINGS = {
    'BCX' : [{"permissable_carrying_capacity":55.5}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BCXC' : [{"permissable_carrying_capacity":55.5}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BCXR' : [{"permissable_carrying_capacity":55.5}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BCXT' : [{"permissable_carrying_capacity":55.5}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BCXN' : [{"permissable_carrying_capacity":55.5}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BCN' : [{"permissable_carrying_capacity":58.0}, {"number_of_wagons":43}, {"container_size":'20'}],
    'BCNA' : [{"permissable_carrying_capacity":58.8}, {"number_of_wagons":43}, {"container_size":'20'}],
    'BCNAHS' : [{"permissable_carrying_capacity":58.8}, {"number_of_wagons":43}, {"container_size":'20'}],
    'BOXNHA' : [{"permissable_carrying_capacity":60.1}, {"number_of_wagons":43}, {"container_size":'20'}],
    'BOXN' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOXNHS' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOI' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BRS' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BRH' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BRN' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOBS' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOBSN' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOBX' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOBY' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOBYN' : [{"permissable_carrying_capacity":58}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOX' : [{"permissable_carrying_capacity":60}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOST' : [{"permissable_carrying_capacity":60}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOBR' : [{"permissable_carrying_capacity":60}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BTNP': [{"permissable_carrying_capacity":60}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BTALN': [{"permissable_carrying_capacity":60}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BTPGLN': [{"permissable_carrying_capacity":60}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BTCS': [{"permissable_carrying_capacity":60}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BTPN': [{"permissable_carrying_capacity":54.28}, {"number_of_wagons":47}, {"container_size":'20'}],
    'BTAP': [{"permissable_carrying_capacity":54.28}, {"number_of_wagons":47}, {"container_size":'20'}],
    'BCNAHS': [{"permissable_carrying_capacity":56.73}, {"number_of_wagons":43}, {"container_size":'20'}],
    'BRNA-EUR': [{"permissable_carrying_capacity":56.73}, {"number_of_wagons":18}, {"container_size":'20'}],
    'BFNSM': [{"permissable_carrying_capacity":56.73}, {"number_of_wagons":68}, {"container_size":'40HC'}],
    'BOXNHL': [{"permissable_carrying_capacity":71.05}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOXNHS': [{"permissable_carrying_capacity":58.08}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BCNHL': [{"permissable_carrying_capacity":70.8}, {"number_of_wagons":58}, {"container_size":'40'}],
    'BOXNS': [{"permissable_carrying_capacity":80.15}, {"number_of_wagons":59}, {"container_size":'40'}],
    'BOY': [{"permissable_carrying_capacity":70.89}, {"number_of_wagons":52}, {"container_size":'40'}],
    'BRNA': [{"permissable_carrying_capacity":57.7}, {"number_of_wagons":43}, {"container_size":'20'}],
    'BFNS': [{"permissable_carrying_capacity":70.8}, {"number_of_wagons":54}, {"container_size":'40'}],
}

CONTAINER_SIZE_WAGON_MAPPING = {

}

# CONTAINER_TYPE_COMMODITY_MAPPINGS = {
#     'standard' => [nil] + GlobalConstants::HAZ_CLASSES + RailDomesticFreightConstants::COMMODITY,
#     'refer' => [nil] + RailDomesticFreightConstants::COMMODITY,
#     'open_top' => [nil] + RailDomesticFreightConstants::COMMODITY,
#     'open_side' => [nil] + RailDomesticFreightConstants::COMMODITY,
#     'flat_rack' => [nil] + RailDomesticFreightConstants::COMMODITY,
#     'iso_tank' => [nil] + GlobalConstants::HAZ_CLASSES + RailDomesticFreightConstants::COMMODITY,
#     'conventional_end_opening' => RailDomesticFreightConstants::COMMODITY,
#     'high_cube_end_opening' => RailDomesticFreightConstants::COMMODITY,
#     'side_access' => RailDomesticFreightConstants::COMMODITY,
#     'refrigerated' => RailDomesticFreightConstants::COMMODITY,
#     'flat_rack_collapsible' => RailDomesticFreightConstants::COMMODITY,
#     'platform' => RailDomesticFreightConstants::COMMODITY,
#     'tank' => RailDomesticFreightConstants::COMMODITY,
#     'high_cube_refrigerated' => RailDomesticFreightConstants::COMMODITY,
#     'ss_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ms_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ss_volve_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ms_volve_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ss_blank_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ms_blank_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ss_hc_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ms_hc_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ss_blank_hc_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ms_blank_hc_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ss_normal_tank' => RailDomesticFreightConstants::COMMODITY,
#     'ms_normal_tank' => RailDomesticFreightConstants::COMMODITY
#   }
