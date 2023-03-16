def find_or_initialize(Model,**kwargs):
  try:
    obj = Model.get(**kwargs)
    obj.updated_at = Model.datetime.now()##############
  except Model.DoesNotExist:
    obj = Model(**kwargs)
  return obj

  