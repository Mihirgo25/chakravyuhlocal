from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit

def get_relevant_rate_ids(rate_sheet_id, apply_to_extended_rates, object_ids):
    if object_ids and not isinstance(object_ids, list):
        object_ids = [object_ids]

    query = FclFreightRateAudit.select(FclFreightRateAudit.object_id)
    if(rate_sheet_id and apply_to_extended_rates and object_ids):
        query = query.where((FclFreightRateAudit.rate_sheet_id == rate_sheet_id) | (FclFreightRateAudit.extended_from_object_id << object_ids)) 
    elif rate_sheet_id and not (apply_to_extended_rates or object_ids):
        query = query.where(FclFreightRateAudit.rate_sheet_id == rate_sheet_id)
    elif not rate_sheet_id and apply_to_extended_rates and object_ids:
        query = query.where(FclFreightRateAudit.extended_from_object_id << object_ids) 
    else:
        return []

    return [str(result['object_id']) for result in (query.dicts())]

def is_price_in_range(lower_limit,upper_limit, price):
    
    if lower_limit is not None and price <= lower_limit:
        return False

    if upper_limit is not None and price >= upper_limit:
        return False

    return True