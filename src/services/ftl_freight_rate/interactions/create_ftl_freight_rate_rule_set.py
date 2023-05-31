from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import FtlFreightRateRuleSet
from fastapi import HTTPException
from database.db_session import db
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit


def get_extension_rule_set_object(request):
    row = {
        'location_id' : request.get('location_id'),
        'location_type' : request.get('location_type'),
        'truck_type' : request.get('truck_type'),
        'process_type' : request.get('process_type'),
        'process_unit' : request.get('process_unit'),
        'process_value' : request.get('process_value'),
        'process_currency' : request.get('process_currency'),
        'status' : request.get('status')
    }

    extension_rule_set = FtlFreightRateRuleSet.select().where(
        FtlFreightRateRuleSet.location_id == request.get('location_id'),
        FtlFreightRateRuleSet.location_type == request.get('location_type'),
        FtlFreightRateRuleSet.truck_type == request.get('truck_type'),
        FtlFreightRateRuleSet.process_type == request.get('process_type')).first()

    if not extension_rule_set:
        extension_rule_set = FtlFreightRateRuleSet(**row)
    else:
        raise HTTPException(status_code=500, detail='ftl rule set already exist')

    extension_rule_set.status = 'active'

    return extension_rule_set

def create_ftl_rule_set_data(request):
  with db.atomic():
    return execute_transaction_code(request)


def execute_transaction_code(request):
  rule_set = get_extension_rule_set_object(request)

  try:
      rule_set.save()
  except:
      raise HTTPException(status_code=500, detail='ftl rule set did not save')

  create_audit(request,rule_set.id)

  return {"id": rule_set.id}

def create_audit(request, rule_set_id):
    data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id'] and not value == None}
    FtlServiceAudit.create(
        action_name = 'create',
        performed_by_id = request.get('performed_by_id'),
        data = data,
        object_id = rule_set_id,
        object_type = 'FtlFreightRateRuleSet'
    )
