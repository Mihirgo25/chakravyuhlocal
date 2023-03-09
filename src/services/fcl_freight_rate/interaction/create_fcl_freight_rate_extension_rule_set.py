from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSets
from fastapi import HTTPException
from database.db_session import db
import time

def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRateExtensionRuleSets.get(**kwargs)
  except FclFreightRateExtensionRuleSets.DoesNotExist:
    obj = FclFreightRateExtensionRuleSets.create(**kwargs)
  return obj

def get_extension_rule_set_object(request):
  request = request.__dict__
  extension_rule_set = find_or_initialize(**request)

  extra_fields = ['cluster_id','gri_rate','gri_currency']
  for field in extra_fields:
      if field in request:
          setattr(extension_rule_set, field, request[field])

  setattr(extension_rule_set, 'status', 'active')

  return extension_rule_set

def create_fcl_freight_rate_extension_rule_set_data(request):
  with db.atomic() as transaction:
    try:
      data = execute(request)
      return data
    except Exception as e:
      transaction.rollback()
      return "Creation Failed"

def execute(request):
  rule_set = get_extension_rule_set_object(request)
  validity = rule_set.validate_all()
  try:
    if validity:
      rule_set.save()
    else:
      raise Exception('Validation error')
  except:
      raise HTTPException(status_code=499, detail='fcl freight rate exclusive rule set did not save')
  return {"id": rule_set.id}