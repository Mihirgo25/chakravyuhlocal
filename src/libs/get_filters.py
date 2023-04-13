from operator import attrgetter


def get_filters(filters: dict, query, model):
    filter_keys = list(filters.keys())

    for filter_key in filter_keys:
        filter_value = filters[filter_key]

        if isinstance(filter_value, int):
            query = query.where(attrgetter(filter_key)(model) == filter_value)
        elif isinstance(filter_value, str):
            if filter_value != "":
                query = query.where(attrgetter(filter_key)(model) == filter_value)
        elif isinstance(filter_value, bool):
                if filter_value:
                    query = query.where(attrgetter(filter_key)(model))
                else:
                    query = query.where(~attrgetter(filter_key)(model))
        elif isinstance(filter_value, list):
            if 'None' in filter_value:
                filter_value.remove('None')
            query = query.where(attrgetter(filter_key)(model) << filter_value)
        elif isinstance(filter_value, (str, type(None))):
            query = query.where(attrgetter(filter_key)(model) == filter_value)
    return query
