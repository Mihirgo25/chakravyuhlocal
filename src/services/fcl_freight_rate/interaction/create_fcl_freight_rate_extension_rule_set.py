from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSets
from fastapi import HTTPException
from database.db_session import db
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit

# def find_or_initialize(**kwargs):
#   try:
#     obj = FclFreightRateExtensionRuleSets.get(**kwargs)
#   except FclFreightRateExtensionRuleSets.DoesNotExist:
#     obj = FclFreightRateExtensionRuleSets.create(**kwargs)
#   return obj

def get_extension_rule_set_object(request):
  extension_rule_set = find_or_initialize(FclFreightRateExtensionRuleSets,**request)

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
  request = request.__dict__
  data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id'] and not value == None}
  rule_set = get_extension_rule_set_object(data)
  rule_set.validate_all()
  try:
      rule_set.save()
  except:
      raise HTTPException(status_code=499, detail='fcl freight rate exclusive rule set did not save')
  create_audit(data, request['performed_by_id'])
  return {"id": rule_set.id}

def create_audit(data, performed_by_id):
    FclFreightRateAudit.create(
    action_name = 'create',
    performed_by_id = performed_by_id,
    data = data,
    object_type = 'FclFreightRateExtensionRuleSets'
    )