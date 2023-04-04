from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from configs.fcl_freight_rate_constants import LOCATION_HIERARCHY
import json
from fastapi.encoders import jsonable_encoder

possible_direct_filters = ['location_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id', 'local_service_provider_ids', 'importer_exporter_id', 'specificity_type','free_limit', 'validity_start', 'validity_end']

def get_most_eligible_free_days(data, filters):  
    data = sorted(data, key=lambda t: [
        LOCATION_HIERARCHY[t['location_type']],
        0 if filters['service_provider_id'] == t['service_provider_id'] else 1,
        (lambda x: 
        0 if x == 'shipping_line' else 
        1 if x == 'cogoport' else 
        2
        )
        (t['specificity_type']) if t['service_provider_id'] in filters['local_service_provider_ids'] else 
    (lambda x: 
        0 if x == 'rate_specific' else 
        1 if x == 'shipping_line' else 
        2 if x == 'cogoport' else 
        3
    )(t['specificity_type'])])

    free_days = data[0] if data else None
    return free_days

def get_eligible_fcl_freight_rate_free_day(filters, freight_rates,sort_by_specificity_type = False):
    if not filters:
        return {}

    if type(filters) != dict:
        filters = json.loads(filters)

    if not all_fields_present(filters):
        return {}

    all_service_provider_ids = list(set(filters["service_provider_id"] + filters["local_service_provider_ids"]))
    
    query = FclFreightRateFreeDay.select(
        FclFreightRateFreeDay.id,
        FclFreightRateFreeDay.location_id,
        FclFreightRateFreeDay.trade_type,
        FclFreightRateFreeDay.free_days_type,
        FclFreightRateFreeDay.shipping_line_id,
        FclFreightRateFreeDay.service_provider_id,
        FclFreightRateFreeDay.specificity_type,
        FclFreightRateFreeDay.location_type,
        FclFreightRateFreeDay.free_limit,
        FclFreightRateFreeDay.slabs,
        FclFreightRateFreeDay.is_slabs_missing,
        FclFreightRateFreeDay.previous_days_applicable,
        FclFreightRateFreeDay.remarks,
        FclFreightRateFreeDay.rate_not_available_entry
    ).where(
        ((FclFreightRateFreeDay.rate_not_available_entry.is_null(True)) | (~FclFreightRateFreeDay.rate_not_available_entry)),
        FclFreightRateFreeDay.location_id == filters['location_id'],
        FclFreightRateFreeDay.trade_type == filters['trade_type'],
        FclFreightRateFreeDay.free_days_type == filters['free_days_type'],
        FclFreightRateFreeDay.container_size == filters['container_size'],
        FclFreightRateFreeDay.container_type == filters['container_type'],
        FclFreightRateFreeDay.shipping_line_id << filters['shipping_line_id'],
        FclFreightRateFreeDay.service_provider_id << all_service_provider_ids
    )
    if 'importer_exporter_id' in filters:
        query = query.where(((FclFreightRateFreeDay.importer_exporter_id == filters['importer_exporter_id']) | (FclFreightRateFreeDay.importer_exporter_id == None)))
    
    if 'free_limit' in filters:
        query = query.where(FclFreightRateFreeDay.free_limit == filters['free_limit'])

    if 'validity_start' in filters and 'validity_end' in filters:
        query = query.where(FclFreightRateFreeDay.validity_start <= filters['validity_start'] and FclFreightRateFreeDay.validity_end >= filters['validity_end'])
        
    data = jsonable_encoder(list(query.dicts()))
    
    if sort_by_specificity_type:
        return sorted(data, key=lambda t: [
            0 if t['specificity_type'] == 'rate_specific' else 
            1 if t['specificity_type'] == 'shipping_line' else 2])

    if freight_rates:
        group_by_rate = {}
        for rate in freight_rates:
            all_rates = []
            key = rate["id"]
            sp_id = rate["service_provider_id"]
            trade_type = filters['trade_type']
            local = rate["destination_local"]
            if trade_type == 'export':
                local = rate["origin_local"]
            for free_day_row in data:
                if (free_day_row['service_provider_id'] ==  sp_id and free_day_row['shipping_line_id'] == rate["shipping_line_id"]) or (free_day_row['service_provider_id'] ==  (local or {}).get("service_provider_id") and free_day_row['shipping_line_id'] == (local or {}).get("shipping_line_id")): 
                    all_rates.append(free_day_row)
            eligible_free_days = get_most_eligible_free_days(all_rates, filters)
            group_by_rate[key] = eligible_free_days
        return group_by_rate

    return get_most_eligible_free_days(data, filters)

                  

def all_fields_present(filters):
    for field in ('location_id','trade_type','free_days_type','container_size','container_type','shipping_line_id'):
        if field not in filters:
            return False
    return True