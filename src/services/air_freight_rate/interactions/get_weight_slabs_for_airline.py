from services.air_freight_rate.constants.air_freight_rate_constants import AIRLINE_IDS_WITH_CUSTOM_WEIGHT_SLABS,CUSTOM_WEIGHT_SLABS,DEFAULT_WEIGHT_SLABS

def get_weight_slabs_for_airline(airline_id,chargeable_weight,overweight_upper_limit):
    custom_airlines = AIRLINE_IDS_WITH_CUSTOM_WEIGHT_SLABS

    if airline_id in custom_airlines:
        weight_slabs = CUSTOM_WEIGHT_SLABS
    else:
        weight_slabs = DEFAULT_WEIGHT_SLABS

    if chargeable_weight:
        for weight_slab in weight_slabs:
            if int(weight_slab['lower_limit']) <= chargeable_weight and chargeable_weight < int(weight_slab['upper_limit']):
                return [weight_slab]
        if overweight_upper_limit >0.0:
                    new_lower_limit = int((chargeable_weight / 100))* 100 + 0.1
                    new_upper_limit = int((chargeable_weight / 100)) * 100 + max(overweight_upper_limit, 100)
                    weight_slabs.append({ 'lower_limit' : new_lower_limit, 'upper_limit' : new_upper_limit})
    return weight_slabs