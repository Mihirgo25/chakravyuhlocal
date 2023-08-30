def get_identifier(rate_id, validity_id) -> str:
    return "".join([rate_id, validity_id]).replace("-", "")

def get_air_freight_identifier(rate_id,validity_id,lower_limit,upper_limit) -> str:
    return "".join([rate_id, validity_id, str(lower_limit), str(upper_limit)]).replace("-","")
