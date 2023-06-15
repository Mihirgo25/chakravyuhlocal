from models.fcl_freight_rate_audit import FclFreightRateAudit

def get_rate_ids(select_field, id):
    reference_object_ids = FclFreightRateAudit.select(getattr(FclFreightRateAudit, select_field)).where(FclFreightRateAudit.object_id == id)
    reference_object_ids = [audit_data[select_field] for audit_data in list(reference_object_ids.dicts())] 
    
    rate_ids = FclFreightRateAudit.select(FclFreightRateAudit.object_id).where(getattr(FclFreightRateAudit, select_field) << reference_object_ids)
    rate_ids = [str(result['object_id']) for result in (rate_ids.dicts())]
    return rate_ids