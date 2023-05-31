from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_cfs_rate.models.fcl_cfs_audits import FclCfsRateAudits
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate_platform_prices import update_platform_prices_for_other_service_providers

def get_audit_params(request):
    audit_data = {
        "line_items": request.line_items,
        "free_days": request.free_days
    }

    return {
        'action_name': 'update',
        'performed_by_id': request["performed_by_id"],
        'bulk_operation_id': request["bulk_operation_id"],
        'sourced_by_id': request["sourced_by_id"],
        'procured_by_id': request["procured_by_id"],
        'data': audit_data
    }

def update_fcl_cfs_rate(request):
    freight_id = request["id"]

    freight = FclCfsRate.get_or_none(id=freight_id)

    if not freight:
        return 'id is invalid'

    FclCfsRate.set_platform_price()
    FclCfsRate.set_is_best_price()
    FclCfsRate.update_line_item_messages()
    
    
    audit_params = get_audit_params(request)
    FclCfsRateAudits.create(**audit_params)
    
    freight.update_platform_prices_for_other_service_providers()
    

    freight.save()

    return {'id': freight.id}
