CONTAINR_TYPE_FACTORS = {
    'standard': 1,
    'refer': 3,
    'open_top': 2,
    'flat_rack': 2,
    'open_side': 2, 
    'iso_tank': 2.5
    
}

CONTAINER_SIZE_FACTORS = {
    '20': 1,
    '40': 1.5,
    '40HC': 1.5,
    '45HC': 2
}

HANDLING_TYPE_FACTORS = {
    'stackable': 1,
    'non_stackable': 1
}

PACKING_TYPE_FACTORS = {
    'pallet': 1,
    'box': 1,
    'crate': 1,
    'loose': 1
}

OPERATION_TYPE_FACTORS = {
    'passenger': 1,
    'freighter': 1
}

CHINA_MINIMUM_RATES = {
    '20': {
        'HAZ': {
            'standard': 2000,
            'refer': 4875,
            'open_top': 2875,
            'flat_rack': 2875,
            'open_side': 2875, 
            'iso_tank': 2875
        },
        'NON_HAZ': {
            'standard': 1150,
            'refer': 4025,
            'open_top': 2000,
            'flat_rack': 2000,
            'open_side': 2000, 
            'iso_tank': 2000
        }
    },
    '40': {
        'HAZ': {
            'standard': 2500,
            'refer': 5375,
            'open_top': 3750,
            'flat_rack': 3750,
            'open_side': 3750, 
            'iso_tank': 3750
        },
        'NON_HAZ': {
            'standard': 1250,
            'refer': 4375,
            'open_top': 2500,
            'flat_rack': 2500,
            'open_side': 2500, 
            'iso_tank': 2500
        }
    },
    '40HC': {
        'HAZ': {
            'standard': 2500,
            'refer': 5375,
            'open_top': 3750,
            'flat_rack': 3750,
            'open_side': 3750, 
            'iso_tank': 3750
        },
        'NON_HAZ': {
            'standard': 1250,
            'refer': 4375,
            'open_top': 2500,
            'flat_rack': 2500,
            'open_side': 2500, 
            'iso_tank': 2500
        }
    },
    '45HC': {
        'HAZ': {
            'standard': 2500,
            'refer': 5375,
            'open_top': 3750,
            'flat_rack': 3750,
            'open_side': 3750, 
            'iso_tank': 3750
        },
        'NON_HAZ': {
            'standard': 1250,
            'refer': 4375,
            'open_top': 2500,
            'flat_rack': 2500,
            'open_side': 2500, 
            'iso_tank': 2500
        }
    }
}