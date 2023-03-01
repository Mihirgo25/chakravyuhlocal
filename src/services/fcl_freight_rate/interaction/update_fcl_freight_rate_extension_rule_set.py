from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSets

def update_fcl_freight_rate_extension_rule_set_data(request):
    request = request.__dict__
    # print(request)
    fcl_rule_set = FclFreightRateExtensionRuleSets.get_by_id(request['id'])
    get_update_params = {key:value for key,value in request.items() if key not in ['id','performed_by_id']}
    FclFreightRateExtensionRuleSets.update(get_update_params).where(FclFreightRateExtensionRuleSets.id == fcl_rule_set).execute()
    # print('fcl: ',FclFreightRateExtensionRuleSets.select().where(FclFreightRateExtensionRuleSets.id == fcl_rule_set.id))
    # fcl_rule_set['extension_name'] = request['extension_name']
    # fcl_rule_set['service_provider_id'] = request['service_provider_id']
    # fcl_rule_set['shipping_line_id'] = request['shipping_line_id']
    # fcl_rule_set['cluster_id'] = request['cluster_id']
    # fcl_rule_set['cluster_type'] = request['cluster_type']
    # fcl_rule_set['cluster_reference_name'] = request['cluster_reference_name']
    # fcl_rule_set['line_item_charge_code'] = request['line_item_charge_code']
    # fcl_rule_set['gri_currency'] = request['gri_currency']
    # fcl_rule_set['gri_rate'] = request['gri_rate']
    # fcl_rule_set['status'] = request['status']
    # fcl_rule_set['trade_type'] = request['trade_type']