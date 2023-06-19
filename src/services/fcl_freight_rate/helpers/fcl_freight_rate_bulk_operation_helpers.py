from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.rate_sheet.models.rate_sheet import RateSheet
from micro_services.client import common

def get_relevant_rate_ids_from_audits(rate_sheet_id, apply_to_extended_rates, object_ids):
    if not isinstance(object_ids, list):
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

def is_price_in_range(lower_limit,upper_limit, price,markup_currency,currency):

    if  currency and markup_currency!=currency :
        price=common.get_money_exchange_for_fcl({"price": price, "from_currency": currency, "to_currency": markup_currency })['price']

    if lower_limit is not None and price <= lower_limit:
        return False
    if upper_limit is not None and price >= upper_limit:
        return False
    return True

def get_rate_sheet_id(rate_sheet_serial_no):
    rate_sheet_id=RateSheet.select(RateSheet.id).where(RateSheet.serial_id==rate_sheet_serial_no).first()
    return rate_sheet_id
