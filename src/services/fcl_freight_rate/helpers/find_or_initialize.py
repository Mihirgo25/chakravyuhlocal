def find_or_initialize(Model,**kwargs):
    try:
        model = Model.get(**kwargs)
        return model
    except Model.DoesNotExist:
        return Model(**kwargs)
    