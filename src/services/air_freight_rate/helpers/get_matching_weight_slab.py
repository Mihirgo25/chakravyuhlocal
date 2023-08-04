def get_matching_slab( lower_limit):
    lower_limits = {
        0: "0.0-45",
        45.1: "45-100",
        100.1: "100-300",
        300.1: "300-500",
        500.1: "500-5000",
    }
    weight_slab = ""
    difference = 1000001
    for key, value in lower_limits.items():
        if abs(key - lower_limit) <= difference:
            weight_slab = value
            difference = abs(key - lower_limit)
    return weight_slab