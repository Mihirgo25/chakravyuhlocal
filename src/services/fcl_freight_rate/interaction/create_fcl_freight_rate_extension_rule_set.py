from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSet
from fastapi import HTTPException
from database.db_session import db
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from celery_worker import update_multiple_service_objects
def get_extension_rule_set_object(request):
  row = {
      'extension_name' : request['extension_name'],
      'service_provider_id' : request['service_provider_id'],
      'shipping_line_id' : request.get('shipping_line_id'),
      'cluster_type' : request['cluster_type'],
      'cluster_reference_name' : request['cluster_reference_name'],
      'line_item_charge_code' : request.get('line_item_charge_code'),
      'trade_type' : request.get('trade_type')
    }
  
  extension_rule_set = FclFreightRateExtensionRuleSet.select().where(
      FclFreightRateExtensionRuleSet.extension_name == request['extension_name'],
      FclFreightRateExtensionRuleSet.service_provider_id == request.get('service_provider_id'),
      FclFreightRateExtensionRuleSet.shipping_line_id == request.get('shipping_line_id'),
      FclFreightRateExtensionRuleSet.cluster_type == request['cluster_type'],
      FclFreightRateExtensionRuleSet.cluster_reference_name == request['cluster_reference_name'],
      FclFreightRateExtensionRuleSet.line_item_charge_code == request.get('line_item_charge_code'),
      FclFreightRateExtensionRuleSet.trade_type == request.get('trade_type')).first()

  if not extension_rule_set:
    extension_rule_set = FclFreightRateExtensionRuleSet(**row)

  extra_fields = ['cluster_id','gri_rate','gri_currency']
  for field in extra_fields:
      if field in request:
          setattr(extension_rule_set, field, request[field])

  extension_rule_set.status = 'active'

  return extension_rule_set

def create_fcl_freight_rate_extension_rule_set_data(request):
  object_type = 'Fcl_Freight_Rate_Extension_Rule_Set'
  query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
  db.execute_sql(query)
  with db.atomic():
    return execute_transaction_code(request)


def execute_transaction_code(request):

  data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id'] and not value == None}

  rule_set = get_extension_rule_set_object(data)
  rule_set.validate_all()

  try:
      rule_set.save()
  except:
      raise HTTPException(status_code=500, detail='fcl freight rate exclusive rule set did not save')

  update_multiple_service_objects.apply_async(kwargs={'object':rule_set},queue='low')
  create_audit(data, request['performed_by_id'], rule_set.id)

  return {"id": rule_set.id}

def create_audit(data, performed_by_id, rule_set_id):
  FclServiceAudit.create(
  action_name = 'create',
  performed_by_id = performed_by_id,
  data = data,
  object_id = rule_set_id,
  object_type = 'FclFreightRateExtensionRuleSet'
  )
