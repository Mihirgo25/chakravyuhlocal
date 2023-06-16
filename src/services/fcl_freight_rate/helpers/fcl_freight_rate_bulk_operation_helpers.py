from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit

def get_rate_ids(select_field, id):
    reference_object_ids = FclFreightRateAudit.select(getattr(FclFreightRateAudit, select_field)).where(FclFreightRateAudit.object_id == id)
    reference_object_ids = [audit_data[select_field] for audit_data in list(reference_object_ids.dicts())] 
    
    rate_ids = FclFreightRateAudit.select(FclFreightRateAudit.object_id).where(getattr(FclFreightRateAudit, select_field) << reference_object_ids)
    rate_ids = [str(result['object_id']) for result in (rate_ids.dicts())]
    return rate_ids

def is_price_in_range(lower_limit,upper_limit, price):
    
    if lower_limit is not None and price <= lower_limit:
        return False

    if upper_limit is not None and price >= upper_limit:
        return False

    return True