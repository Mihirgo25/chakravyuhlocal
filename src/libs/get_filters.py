from operator import attrgetter
from playhouse.postgres_ext import ArrayField


def get_filters(filters: dict, query, model):
    filter_keys = list(filters.keys())

    for filter_key in filter_keys:
        filter_value = filters[filter_key]

        if isinstance(filter_value, bool):

            if filter_value:
                query = query.where(attrgetter(filter_key)(model))
            else:
                query = query.where(~attrgetter(filter_key)(model))
        elif isinstance(filter_value, str) or isinstance(filter_value, int):
            if filter_value != "":
                query = query.where(attrgetter(filter_key)(model) == filter_value)
        elif isinstance(filter_value, list):
            if 'None' in filter_value:
                filter_value.remove('None')
            attribute = getattr(model, filter_key)
            if isinstance(attribute, ArrayField):
                query = query.where(attrgetter(filter_key)(model).contains(filter_value))
            else:
                query = query.where(attrgetter(filter_key)(model) << filter_value)

        elif isinstance(filter_value, (str, type(None))):
            query = query.where(attrgetter(filter_key)(model) == filter_value)
    return query
