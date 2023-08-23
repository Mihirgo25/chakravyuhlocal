def filter_predicted_or_extension_rates(freight_rates):
    filtered_rates = ['expired_extention','rate_extension']
    supply_rates = []
    for freight_rate in freight_rates:
        if freight_rate['source'] not in filtered_rates:
            supply_rates.append(freight_rate)
    
    if len(supply_rates)!=0:
        return supply_rates
    return freight_rates
