import uuid

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
    
def get_applicable_filters(filters, POSSIBLE_DIRECT_FILTERS=[], POSSIBLE_INDIRECT_FILTERS=[]):
    direct_filters = {}
    indirect_filters = {}
    for key, val in filters.items():
        if key in POSSIBLE_DIRECT_FILTERS:
            direct_filters[key] = val
        if key in POSSIBLE_INDIRECT_FILTERS:
            indirect_filters[key] = val
    for type in [
        "id",
        "continent_id",
        "trade_id",
        "country_id",
        "region_id",
        "city_id",
        "cluster_id",
        "pincode_id",
        "port_id",
        "airport_id",
        "origin_continent_id",
        "origin_trade_id",
        "origin_country_id",
        "origin_region_id",
        "origin_city_id",
        "origin_cluster_id",
        "origin_pincode_id",
        "origin_port_id",
        "origin_airport_id",
        "destination_continent_id",
        "destination_trade_id",
        "destination_country_id",
        "destination_region_id",
        "destination_city_id",
        "destination_cluster_id",
        "destination_pincode_id",
        "destination_port_id",
        "destination_airport_id",
    ]:
        if type in direct_filters:
            if isinstance(direct_filters[type], str):
                if not is_valid_uuid(direct_filters[type]):
                    del direct_filters[type]
            elif isinstance(direct_filters[type], list):
                for key in direct_filters[type]:
                    if not is_valid_uuid(key):
                        direct_filters[type].remove(key)
    return direct_filters, indirect_filters