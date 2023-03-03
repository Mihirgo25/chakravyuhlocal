from operator import attrgetter

def get_filters(filters: dict, query, model, ilike_string: str):
    filter_keys = list(filters.keys())

    for filter_key in filter_keys:
        filter_value = filters[filter_key]

        if isinstance(filter_value, str):
            if filter_value != "":
                query = query.where(attrgetter(filter_key)(model) == filter_value)
        elif isinstance(filter_value, list):
            if 'None' in filter_value:
                filter_value.remove('None')
            query = query.where(attrgetter(filter_key)(model) << filter_value)
    return query
