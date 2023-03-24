from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSets
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db

def update_fcl_freight_rate_extension_rule_set_data(request):
    with db.atomic() as transaction:
        try:
            execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            raise e

def execute_transaction_code(request):
    
    fcl_rule_set = FclFreightRateExtensionRuleSets.get_by_id(request['id'])
    get_update_params = {key:value for key,value in request.items() if key not in ['id','performed_by_id']}
    FclFreightRateExtensionRuleSets.update(get_update_params).where(FclFreightRateExtensionRuleSets.id == fcl_rule_set).execute()
    create_audit(get_update_params, request['id'], request['performed_by_id'])

def create_audit(get_update_params, fcl_freight_rate_extension_id, performed_by_id):
    FclServiceAudit.create(
    action_name = 'update',
    performed_by_id = performed_by_id,
    data = get_update_params,
    object_id = fcl_freight_rate_extension_id,
    object_type = 'FclFreightRateExtensionRuleSets'
    )