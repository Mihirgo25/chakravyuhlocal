from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet


data_dbcargo= [
    [100, 1301, 1596, 1978, 2466, 3025, 3582, 4082],
    [150, 1557, 2058, 2539, 3010, 3690, 4372, 4985],
    [200, 1759, 2500, 3080, 3650, 4476, 5307, 6048],
    [250, 2068, 2933, 3615, 4298, 5268, 6228, 7114],
    [300, 2288, 3236, 4008, 4757, 5826, 6901, 7860],
    [350, 2585, 3666, 4531, 5377, 6593, 7802, 8897],
    [400, 2783, 3945, 4878, 5783, 7083, 8390, 9570],
    [450, 2933, 4151, 5137, 6093, 7462, 8841, 10076],
    [500, 3126, 4431, 5481, 6502, 7966, 9434, 10753],
    [550, 3309, 4697, 5801, 6888, 8435, 9986, 11381],
    [600, 3483, 4937, 6106, 7240, 8868, 10513, 11978],
    [650, 3654, 5175, 6397, 7586, 9295, 11010, 12553],
    [700, 3821, 5407, 6679, 7927, 9705, 11501, 13107],
    [750, 3944, 5584, 6902, 8184, 10034, 11876, 13539],
    [800, 4031, 5712, 7059, 8367, 10269, 12152, 13856],
    [850, 4117, 5841, 7225, 8565, 10499, 12428, 14168],
    [900, 4208, 5965, 7379, 8751, 10727, 12703, 14481],
    [950, 4302, 6096, 7536, 8935, 10959, 12979, 14790],
    [1000, 4392, 6228, 7698, 9129, 11193, 13240, 15106],
    [1000, 4392, 6228, 7698, 9129, 11193, 13240, 15106],
    [1100, 4530, 6421, 7939, 9405, 11536, 13660, 15566],
    [1200, 4710, 6671, 8255, 9788, 11997, 14210, 16188],
    [1300, 4894, 6938, 8567, 10160, 12454, 14749, 16813]
]

Wagon_types = ["2 axles","More than 2 axles"]
container_weights = [21.5,30.5,34.5,44.5,54.5,64.5,74.5]

def insert_dbcargo_rates():

    for row in data_dbcargo:
        for element in range(1,len(row)):
            if element > 2:
                query = {
                "distance" : row[0],
                "base_price" : row[element],
                "wagon_type" : Wagon_types[1],
                "train_load_type" : "Wagon Load",
                "commodity_class_type" : "default",
                "currency" : "EUR",
                "country_code" : "EU",
                "container_size": container_weights[element - 1]
                }
            
            else:
                query = {
                "distance" : row[0],
                "base_price" : row[element],
                "wagon_type" : Wagon_types[0],
                "train_load_type" : "Wagon Load",
                "commodity_class_type" : "default",
                "currency" : "EUR",
                "country_code" : "EU",
                "container_size": container_weights[element - 1]
                }
            
            HaulageFreightRateRuleSet.create(**query)