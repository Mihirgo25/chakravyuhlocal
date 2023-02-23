from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSets
from operator import attrgetter
from fastapi import HTTPException
from database.db_session import db

def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRateExtensionRuleSets.get(**kwargs)
  except FclFreightRateExtensionRuleSets.DoesNotExist:
    obj = FclFreightRateExtensionRuleSets.create(**kwargs)
  return obj

def get_extension_rule_set_object(request):
  request = request.__dict__
  print('request:',request)
  extension_rule_set = find_or_initialize(**request)
  print('find_or_init', extension_rule_set)

  extra_fields = ['cluster_id','gri_rate','gri_currency']
  for field in extra_fields:
      if field in request:
          setattr(extension_rule_set, field, request[field])

  setattr(extension_rule_set, 'status', 'active')

  return extension_rule_set

def create_fcl_freight_rate_extension_rule_set_data(request):
  # with db.atomic() as transaction:
  #       try:
  #         data = execute(request)
  #         return data
  #       except Exception as e:
  #           transaction.rollback()
  #           return "Creation Failed"
  data = execute(request)
  return data

def execute(request):
  rule_set = get_extension_rule_set_object(request)
  validity = rule_set.validate_all(request)
  try:
    if validity:
      rule_set.save()
    else:
      return {'Validation error'}
  except:
      raise HTTPException(status_code=499, detail='fcl freight rate exclusive rule set did not save')
  print('free_day.id', rule_set)
  return {"id": rule_set.id}