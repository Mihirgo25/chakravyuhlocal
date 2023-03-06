def find_or_initialize(Model,**kwargs):
    try:
        return Model.get(**kwargs)
    except Model.DoesNotExist:
        return Model(**kwargs)
    