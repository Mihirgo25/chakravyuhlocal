from operator import attrgetter
    
def apply_direct_filters(query, filters, possible_direct_filters, Model):  
    for key in filters:
        if key in possible_direct_filters:
            query = query.where(attrgetter(key)(Model) == filters[key])
    return query