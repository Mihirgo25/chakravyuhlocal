from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.rate_sheet.models.rate_sheet import RateSheet
from micro_services.client import common
from database.db_session import rd
from libs.parse_numeric import parse_numeric

def get_relevant_rate_ids_from_audits_for_rate_sheet(rate_sheet_id):

    if not rate_sheet_id:
        return []

    if(rate_sheet_id):
        query = FclFreightRateAudit.select(FclFreightRateAudit.object_id).where((FclFreightRateAudit.rate_sheet_id == rate_sheet_id)) 
        return [str(result['object_id']) for result in (query.dicts())]

def get_relevant_rate_ids_for_extended_from_object(apply_to_extended_rates, object_ids):
    
    if not apply_to_extended_rates: 
        return []
    
    if not isinstance(object_ids, list):
        object_ids = [object_ids]
        
    query = FclFreightRateAudit.select(FclFreightRateAudit.object_id).where((FclFreightRateAudit.extended_from_object_id << object_ids)) 
    return [str(result['object_id']) for result in (query.dicts())]
    
    
    
    

def is_price_in_range(lower_limit,upper_limit, price,markup_currency,currency):

    if  currency and markup_currency!=currency :
        price=common.get_money_exchange_for_fcl({"price": price, "from_currency": currency, "to_currency": markup_currency })['price']

    if lower_limit is not None and price <= lower_limit:
        return False
    if upper_limit is not None and price >= upper_limit:
        return False
    return True

def get_rate_sheet_id(rate_sheet_serial_id):
    rate_sheet_id=RateSheet.select(RateSheet.id).where(RateSheet.serial_id==rate_sheet_serial_id).first()
    return rate_sheet_id


def get_progress_percent(id, progress = 0):
    progress_percent_hash = "bulk_operation_progress"
    progress_percent_key =  f"bulk_operations_{id}"
    
    if rd:
        try:
            cached_response = rd.hget(progress_percent_hash, progress_percent_key)
            return max(parse_numeric(cached_response) or 0, progress)
        except:
            return progress
    else: 
        return progress


def get_total_affected_rates(id, total_affected_rates = 0):
    progress_percent_hash = "bulk_operation_progress"
    progress_percent_key =  f"bulk_operations_affected_{id}"
    
    if rd:
        try:
            cached_response = rd.hget(progress_percent_hash, progress_percent_key)
            return max(parse_numeric(cached_response) or 0, total_affected_rates)
        except:
            return total_affected_rates
    else: 
        return total_affected_rates
    
