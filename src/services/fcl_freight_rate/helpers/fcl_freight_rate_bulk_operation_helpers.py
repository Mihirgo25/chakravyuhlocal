from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit

def get_rate_ids(select_field, id):
    reference_object_ids = FclFreightRateAudit.select(getattr(FclFreightRateAudit, select_field)).where(FclFreightRateAudit.object_id == id)
    reference_object_ids = [audit_data[select_field] for audit_data in list(reference_object_ids.dicts())] 
    
    rate_ids = FclFreightRateAudit.select(FclFreightRateAudit.object_id).where(getattr(FclFreightRateAudit, select_field) << reference_object_ids)
    rate_ids = [str(result['object_id']) for result in (rate_ids.dicts())]
    return rate_ids

def is_price_in_range(data,price):
    lower_limit=data.get('rates_greater_than_price')
    upper_limit=data.get('rates_less_than_price')

    if (upper_limit==None and lower_limit==None) or (price>lower_limit and price<upper_limit):
        return True

    return False    