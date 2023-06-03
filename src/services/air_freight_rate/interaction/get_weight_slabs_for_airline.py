

def get_weight_slabs_for_airline(request):
    custom_airlines = []

    if request.get('airline_id') in custom_airlines:
        weight_slabs = []
    else:
        weight_slabs = []

    new_weight_slabs =[]
    if request.get('chargeable_weight'):
        chargeable_weight = request.get('chargeable_weight')
        for weight_slab in weight_slabs:
            if int(weight_slab['lower_limit']) <= chargeable_weight and chargeable_weight < int(weight_slab['upper_limit']):
                new_weight_slabs.append(weight_slab)
    
    return new_weight_slabs


