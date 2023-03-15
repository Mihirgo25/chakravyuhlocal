from operator import attrgetter
from datetime import datetime

def find_or_initialize(Model,**kwargs):
    try:
        obj = Model.get(**kwargs)
        obj.updated_at = datetime.now()  
        return obj
    except Model.DoesNotExist:
        return Model(**kwargs)
    
def apply_direct_filters(query, filters, possible_direct_filters, Model):  
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(Model) == filters[key])
    return query