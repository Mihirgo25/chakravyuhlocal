def filter_predicted_or_extension_rates(freight_rates,service):
    filtered_rates = []
    if service == 'air_freight':
        key = 'source'
        filtered_rates = ['expired_extention','rate_extension']
    elif service == 'fcl_freight':
        filtered_rates = ['expired_extention']
        key = 'mode'
    
    supply_rates = []
    for freight_rate in freight_rates:
        if freight_rate[key] not in filtered_rates:
            supply_rates.append(freight_rate)
    
    if len(supply_rates)!=0:
        return supply_rates
    return freight_rate
