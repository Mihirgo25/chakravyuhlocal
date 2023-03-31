from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSet
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db

def update_fcl_freight_rate_extension_rule_set_data(request):
    object_type = 'Fcl_Freight_Rate_Extension_Rule_Sets' 
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    
    fcl_rule_set = FclFreightRateExtensionRuleSet.get_by_id(request['id'])
    get_update_params = {key:value for key,value in request.items() if key not in ['id','performed_by_id']}
    FclFreightRateExtensionRuleSet.update(get_update_params).where(FclFreightRateExtensionRuleSet.id == fcl_rule_set).execute()
    create_audit(get_update_params, request['id'], request['performed_by_id'])
    return {'id' : fcl_rule_set.id}

def create_audit(get_update_params, fcl_freight_rate_extension_id, performed_by_id):
    FclServiceAudit.create(
    action_name = 'update',
    performed_by_id = performed_by_id,
    data = get_update_params,
    object_id = fcl_freight_rate_extension_id,
    object_type = 'FclFreightRateExtensionRuleSet'
    )