from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSets

def update_fcl_freight_rate_extension_rule_set_data(request):
    request = request.__dict__
    
    fcl_rule_set = FclFreightRateExtensionRuleSets.get_by_id(request['id'])
    get_update_params = {key:value for key,value in request.items() if key not in ['id','performed_by_id']}
    FclFreightRateExtensionRuleSets.update(get_update_params).where(FclFreightRateExtensionRuleSets.id == fcl_rule_set).execute()