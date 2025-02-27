from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from configs.fcl_freight_rate_constants import LOCATION_HIERARCHY, DEFAULT_SERVICE_PROVIDER_ID, SPECIFICITY_TYPE_HIERARCHY
import json
from fastapi.encoders import jsonable_encoder

possible_direct_filters = ['location_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id', 'local_service_provider_ids', 'importer_exporter_id', 'specificity_type','free_limit', 'validity_start', 'validity_end']

def get_most_eligible_free_days(data, filters):
    data = sorted(data, key=lambda t: [
            LOCATION_HIERARCHY[t['location_type']],
            0 if t['service_provider_id'] in filters['service_provider_id'] else 1,
            SPECIFICITY_TYPE_HIERARCHY[t['specificity_type']]
    ])
    free_days = data[0] if data else None
    return free_days

def get_eligible_fcl_freight_rate_free_day(filters, freight_rates=None,sort_by_specificity_type = False):
    if not filters:
        return {}

    if type(filters) != dict:
        filters = json.loads(filters)

    if not all_fields_present(filters):
        return {}
    
    all_service_provider_ids = []

    if isinstance(filters['service_provider_id'],str):
        all_service_provider_ids += [filters["service_provider_id"]]
    else:
        all_service_provider_ids += filters["service_provider_id"]

    if 'local_service_provider_ids' in filters:
        all_service_provider_ids+=filters["local_service_provider_ids"]

    all_service_provider_ids = list(set(all_service_provider_ids))
    all_service_provider_ids.append(DEFAULT_SERVICE_PROVIDER_ID)

    if isinstance(filters['shipping_line_id'],str):
        filters['shipping_line_id'] = [filters['shipping_line_id']]
        
    if isinstance(filters['location_id'],str):
        filters['location_id'] = [filters['location_id']]
    
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
        FclFreightRateFreeDay.location_id.in_(filters['location_id']),
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
        query = query.where(FclFreightRateFreeDay.validity_start.cast('date') <= filters['validity_start'], 
                            FclFreightRateFreeDay.validity_end.cast('date') >= filters['validity_end']
                )
        
    data = jsonable_encoder(list(query.dicts()))
    
    if sort_by_specificity_type:
        return sorted(data, key=lambda t: SPECIFICITY_TYPE_HIERARCHY[t['specificity_type']])

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
                if (free_day_row['service_provider_id'] in [sp_id, DEFAULT_SERVICE_PROVIDER_ID] and free_day_row['shipping_line_id'] == rate["shipping_line_id"]) or (free_day_row['service_provider_id'] ==  (local or {}).get("service_provider_id") and free_day_row['shipping_line_id'] == (local or {}).get("shipping_line_id")): 
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