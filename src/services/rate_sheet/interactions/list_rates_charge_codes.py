from configs.defintions import FCL_FREIGHT_CHARGES

def list_rates_charge_codes(service_name, service_names):
    if not service_names:
        service_names =  [service_name]
    final_list = []
    if 'domestic_air_freight_charges' in service_names:
        service_names.append('domestic_air_freight_surcharges')
    if 'air_freight_charges' in service_names:
        service_names.append('air_freight_surcharges')

    for name in service_names:
        # check this code once
        for key, val in FCL_FREIGHT_CHARGES.get(name).items():
            val['code'] = key
        final_list += FCL_FREIGHT_CHARGES.get(name)

    final_list = remove_codes_with_deleted_tag(final_list)
    return {'list': final_list}

def remove_codes_with_deleted_tag(final_list):
    code_list = list()
    for code in final_list:
        if 'deleted' in code['tags']:
            continue
        code_list.append(code)
    return code_list




