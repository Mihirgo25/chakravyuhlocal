from configs.air_freight_rate_constants import AIRLINE_IDS_WITH_CUSTOM_WEIGHT_SLABS,CUSTOM_WEIGHT_SLABS,DEFAULT_WEIGHT_SLABS

def get_weight_slabs_for_airline(airline_id,chargeable_weight):
    custom_airlines = AIRLINE_IDS_WITH_CUSTOM_WEIGHT_SLABS

    if airline_id in custom_airlines:
        weight_slabs = AIRLINE_IDS_WITH_CUSTOM_WEIGHT_SLABS
    else:
        weight_slabs = CUSTOM_WEIGHT_SLABS

    new_weight_slabs =DEFAULT_WEIGHT_SLABS
    if chargeable_weight:
        for weight_slab in weight_slabs:
            if int(weight_slab['lower_limit']) <= chargeable_weight and chargeable_weight < int(weight_slab['upper_limit']):
                new_weight_slabs.append(weight_slab)
    
    return new_weight_slabs


