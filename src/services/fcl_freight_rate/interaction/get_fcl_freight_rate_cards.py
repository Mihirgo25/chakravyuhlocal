from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.fcl_freight_rate_constants import RATE_ENTITY_MAPPING, DEFAULT_LOCAL_AGENT_IDS, OVERWEIGHT_SURCHARGE_LINE_ITEM, DEFAULT_FREE_DAY_LIMIT, DEFAULT_SHIPPING_LINE_ID
from services.fcl_freight_rate.interaction.get_fcl_freight_weight_slabs_for_rates import get_fcl_freight_weight_slabs_for_rates
from services.fcl_freight_rate.interaction.get_eligible_fcl_freight_rate_free_day import get_eligible_fcl_freight_rate_free_day
from configs.global_constants import HAZ_CLASSES, CONFIRMED_INVENTORY, DEFAULT_PAYMENT_TERM, DEFAULT_MAX_WEIGHT_LIMIT
from configs.definitions import FCL_FREIGHT_CHARGES, FCL_FREIGHT_LOCAL_CHARGES
from datetime import datetime, timedelta
import concurrent.futures
from fastapi.encoders import jsonable_encoder
from services.envision.interaction.get_fcl_freight_predicted_rate import get_fcl_freight_predicted_rate
from database.rails_db import get_shipping_line, get_eligible_orgs
from database.db_session import rd
from services.chakravyuh.consumer_vyuhs.fcl_freight import FclFreightVyuh
import sentry_sdk
import traceback

def initialize_freight_query(requirements, prediction_required = False):
    freight_query = FclFreightRate.select(
    FclFreightRate.id,
    FclFreightRate.origin_continent_id,
    FclFreightRate.origin_trade_id,
    FclFreightRate.destination_continent_id,
    FclFreightRate.destination_trade_id,
    FclFreightRate.validities,
    FclFreightRate.container_size,
    FclFreightRate.container_type,
    FclFreightRate.commodity,
    FclFreightRate.origin_port_id,
    FclFreightRate.destination_port_id,
    FclFreightRate.origin_country_id,
    FclFreightRate.destination_country_id,
    FclFreightRate.origin_main_port_id,
    FclFreightRate.destination_main_port_id,
    FclFreightRate.importer_exporter_id,
    FclFreightRate.service_provider_id,
    FclFreightRate.shipping_line_id,
    FclFreightRate.weight_limit,
    FclFreightRate.origin_local,
    FclFreightRate.destination_local,
    FclFreightRate.is_origin_local_line_items_error_messages_present,
    FclFreightRate.is_destination_local_line_items_error_messages_present,
    FclFreightRate.cogo_entity_id,
    FclFreightRate.mode,
    FclFreightRate.rate_type
    ).where(
    FclFreightRate.origin_port_id == requirements['origin_port_id'],
    FclFreightRate.destination_port_id == requirements['destination_port_id'],
    FclFreightRate.container_size == requirements['container_size'],
    FclFreightRate.container_type == requirements['container_type'],
    FclFreightRate.commodity == requirements['commodity'],
    ~FclFreightRate.rate_not_available_entry,
    ((FclFreightRate.importer_exporter_id == requirements['importer_exporter_id']) | (FclFreightRate.importer_exporter_id == None))
    )
    rate_constant_mapping_key = requirements['cogo_entity_id']

    allow_entity_ids = None
    if rate_constant_mapping_key in RATE_ENTITY_MAPPING:
        allow_entity_ids = RATE_ENTITY_MAPPING[rate_constant_mapping_key]

    if allow_entity_ids:
        freight_query = freight_query.where(((FclFreightRate.cogo_entity_id << allow_entity_ids) | (FclFreightRate.cogo_entity_id.is_null(True))))

    freight_query = freight_query.where(FclFreightRate.last_rate_available_date >= requirements['validity_start'])

    if not prediction_required:
        freight_query  = freight_query.where(((FclFreightRate.mode != 'predicted') | (FclFreightRate.mode.is_null(True))))

    if requirements['ignore_omp_dmp_sl_sps']:
        freight_query = freight_query.where(FclFreightRate.omp_dmp_sl_sp != requirements['ignore_omp_dmp_sl_sps'])

    return freight_query

def is_rate_missing_locals(local_type, rate):
    return not rate[local_type] or 'line_items' not in rate[local_type] or len(rate[local_type]['line_items']) == 0 or rate["is_{}_line_items_error_messages_present".format(local_type)]

def get_rates_which_need_locals(rates):
    rates_need_origin_local = []
    rates_need_destination_local = []

    for rate in rates:
        if is_rate_missing_locals('origin_local', rate):
            rates_need_origin_local.append(rate)
        if is_rate_missing_locals('destination_local', rate):
            rates_need_destination_local.append(rate)

    return { "rates_need_destination_local": rates_need_destination_local, "rates_need_origin_local": rates_need_origin_local }

def get_default_local_agent(country_id = None):
    if not country_id:
        return DEFAULT_LOCAL_AGENT_IDS["default"]["value"]
    return DEFAULT_LOCAL_AGENT_IDS[country_id]["value"]

def get_missing_local_rates(requirements, origin_rates, destination_rates):
    port_ids = [requirements["origin_port_id"], requirements["destination_port_id"]]
    container_size = requirements['container_size']
    container_type = requirements['container_type']
    commodity = requirements['commodity']
    commodity = commodity if commodity in HAZ_CLASSES else None
    main_port_ids = []
    shipping_line_ids = [DEFAULT_SHIPPING_LINE_ID]

    local_default_service_provider = get_default_local_agent()
    service_provider_ids = {}
    service_provider_ids[local_default_service_provider] = True
    for rate in origin_rates:
        if rate["service_provider_id"]:
            service_provider_ids[rate["service_provider_id"]] = True
        if rate["origin_main_port_id"]:
            main_port_ids.append(rate["origin_main_port_id"])
        shipping_line_ids.append(rate["shipping_line_id"])

    for rate in destination_rates:
        if rate["service_provider_id"]:
            service_provider_ids[rate["service_provider_id"]] = True
        if rate["destination_main_port_id"]:
            main_port_ids.append(rate["destination_main_port_id"])
        shipping_line_ids.append(rate["shipping_line_id"])

    all_rate_locals_query = FclFreightRateLocal.select(
        FclFreightRateLocal.id,
        FclFreightRateLocal.data,
        FclFreightRateLocal.rate_not_available_entry,
        FclFreightRateLocal.line_items,
        FclFreightRateLocal.is_line_items_error_messages_present,
        FclFreightRateLocal.trade_type,
        FclFreightRateLocal.shipping_line_id,
        FclFreightRateLocal.service_provider_id,
        FclFreightRateLocal.port_id,
        FclFreightRateLocal.main_port_id
        ).where(
        FclFreightRateLocal.port_id << port_ids,
        FclFreightRateLocal.container_size  == container_size,
        FclFreightRateLocal.container_type == container_type,
        FclFreightRateLocal.commodity == commodity,
        FclFreightRateLocal.shipping_line_id << shipping_line_ids,
        FclFreightRateLocal.service_provider_id << list(service_provider_ids.keys()),
        (FclFreightRateLocal.rate_not_available_entry.is_null(True) | (~FclFreightRateLocal.rate_not_available_entry)),
        (FclFreightRateLocal.is_line_items_error_messages_present.is_null(True) | (~FclFreightRateLocal.is_line_items_error_messages_present))
    )

    if len(main_port_ids) == 2:
        all_rate_locals_query = all_rate_locals_query.where(FclFreightRateLocal.main_port_id << main_port_ids)
    elif len(main_port_ids) == 1:
        all_rate_locals_query = all_rate_locals_query.where((FclFreightRateLocal.main_port_id.is_null(True) | FclFreightRateLocal.main_port_id << main_port_ids))

    all_rate_locals = jsonable_encoder(list(all_rate_locals_query.dicts()))
    
    all_formatted_locals = []
    for local_charge in all_rate_locals:
        new_local_obj = local_charge | {
            "line_items": local_charge["data"]["line_items"]
        }
        all_formatted_locals.append(new_local_obj)
    return all_formatted_locals

def get_matching_local(local_type, rate, local_rates, default_lsp):
    matching_locals = {}
    default_shipping_line_locals = {}
    trade_type = 'export'
    if local_type == 'destination_local':
        trade_type = 'import'
    port_id = rate['origin_port_id'] if trade_type == 'export' else rate['destination_port_id']
    shipping_line_id = rate['shipping_line_id']
    main_port_id = None
    if trade_type == 'export' and rate['origin_main_port_id']:
        main_port_id = rate['origin_main_port_id']
    if trade_type == 'import' and rate['destination_main_port_id']:
        main_port_id = rate['destination_main_port_id']

    for local_rate in local_rates:
        if local_rate['trade_type'] == trade_type and local_rate["port_id"] == port_id and (not main_port_id or main_port_id == local_rate["main_port_id"]):
            if shipping_line_id == local_rate['shipping_line_id']:
                matching_locals[local_rate["service_provider_id"]] = local_rate
            if local_rate['shipping_line_id'] == DEFAULT_SHIPPING_LINE_ID:
                default_shipping_line_locals[local_rate["service_provider_id"]] = local_rate
                
    if default_lsp in matching_locals:
        return matching_locals[default_lsp]
    if default_lsp in default_shipping_line_locals:
        return default_shipping_line_locals[default_lsp]
    if rate["service_provider_id"] in matching_locals:
        return matching_locals[rate["service_provider_id"]]
    if rate["service_provider_id"] in default_shipping_line_locals:
        return default_shipping_line_locals[rate["service_provider_id"]]
    return None


def fill_missing_locals_in_rates(freight_rates, local_rates):
    new_freight_rates = []
    local_default_service_provider = get_default_local_agent()
    for freight_rate in freight_rates:
        if is_rate_missing_locals('origin_local', freight_rate):
            freight_rate['origin_local'] = get_matching_local('origin_local', freight_rate, local_rates, local_default_service_provider)
        if is_rate_missing_locals('destination_local', freight_rate):
            freight_rate['destination_local'] = get_matching_local('destination_local', freight_rate, local_rates, local_default_service_provider)

        new_freight_rates.append(freight_rate)
    return new_freight_rates

def is_weight_limit_missing(rate, requirements):
    return ("weight_limit" not in rate) or ("free_limit" not in (rate.get("weight_limit") or {})) or (rate["weight_limit"]["free_limit"] < requirements["cargo_weight_per_container"] and ("slabs" not in rate["weight_limit"] or (not rate['weight_limit']['slabs']) or (rate["weight_limit"]["slabs"][-1] or {}).get("upper_limit") < requirements["cargo_weight_per_container"]))

def get_rates_which_need_free_limit(requirements, freight_rates):
    missing_free_weight_limit = []
    for rate in freight_rates:
        if is_weight_limit_missing(rate, requirements):
            missing_free_weight_limit.append(rate)
    return missing_free_weight_limit

def get_missing_weight_limit(requirements, missing_free_weight_limit):
    return get_fcl_freight_weight_slabs_for_rates(requirements, missing_free_weight_limit)

def get_built_in_slabs(slabs, rate_free_limit, requirements):
    rate_slabs = []
    if requirements['cargo_weight_per_container'] <= rate_free_limit:
        return rate_slabs
    if not slabs:
        rate_slabs = [{
            'lower_limit': rate_free_limit + 0.1,
            'upper_limit': requirements['cargo_weight_per_container'],
            'price': 0,
            'currency': 'USD'
        }]
    else:
        last_slab = slabs[-1]
        rate_slabs = slabs.append({
            'lower_limit': last_slab['upper_limit'] + 0.1,
            'upper_limit': requirements['cargo_weight_per_container'],
            'price': last_slab['price'],
            'currency': last_slab['currency']
        })
    return rate_slabs

def fill_missing_weight_limit_in_rates(freight_rates, weight_limits, requirements):
    new_freight_rates = []
    for rate in freight_rates:
        if rate['id'] in weight_limits:
            weight_limit = weight_limits[rate["id"]]
            if is_weight_limit_missing(rate, requirements):
                rate['weight_limit'] = weight_limit
        new_freight_rates.append(rate)
    
    with_weight_limit_rates = []
    for rate in new_freight_rates:
        if is_weight_limit_missing(rate, requirements):
            free_limit = (rate.get("weight_limit") or {}).get('free_limit')
            slabs = (rate.get("weight_limit") or {}).get('slabs') or []
            rate_free_limit = free_limit or DEFAULT_MAX_WEIGHT_LIMIT[requirements['container_size']]
            rate_slabs = slabs
            rate_slabs = get_built_in_slabs(slabs=slabs, rate_free_limit=rate_free_limit, requirements=requirements)
            rate['weight_limit'] = {
                'free_limit': rate_free_limit,
                'slabs': rate_slabs
            }
            rate_key = 'missing_weight_limit_{}'.format(rate['id'])
            rd.set(name=rate_key, value=1, ex=86400)
        with_weight_limit_rates.append(rate)

    return with_weight_limit_rates


def fill_missing_free_days_in_rates(requirements, freight_rates):
    service_provider_ids = []
    shipping_line_ids = []
    origin_local_service_providers = []
    destination_local_service_providers = []
    for rate in freight_rates:
        shipping_line_ids.append(rate["shipping_line_id"])
        service_provider_ids.append(rate["service_provider_id"])
        if rate["origin_local"] and 'service_provider_id' in rate["origin_local"]:
            origin_local_service_providers.append(rate["origin_local"]["service_provider_id"])
        if rate["destination_local"] and 'service_provider_id' in rate["destination_local"]:
            destination_local_service_providers.append(rate["destination_local"]["service_provider_id"])

    common_filters = {
        "container_size": requirements["container_size"],
        "container_type": requirements["container_type"],
        "shipping_line_id": shipping_line_ids,
        "service_provider_id": service_provider_ids,
        "importer_exporter_id": requirements["importer_exporter_id"],
        "validity_end": (datetime.now() + timedelta(days=60)).date(),
        "validity_start": datetime.now().date()
    }
    origin_detention_filters = common_filters | {
        "location_id": requirements["origin_port_id"],
        "trade_type": "export",
        "free_days_type": "detention",
        "local_service_provider_ids": origin_local_service_providers
    }

    destination_detention_filters = common_filters | {
        "location_id": requirements["destination_port_id"],
        "trade_type": "import",
        "free_days_type": "detention",
        "local_service_provider_ids": destination_local_service_providers
    }

    origin_demurrage_filters = common_filters | {
        "location_id": requirements["origin_port_id"],
        "trade_type": "export",
        "free_days_type": "demurrage",
        "local_service_provider_ids": origin_local_service_providers
    }

    destination_demurrage_filters = common_filters | {
        "location_id": requirements["destination_port_id"],
        "trade_type": "import",
        "free_days_type": "demurrage",
        "local_service_provider_ids": destination_local_service_providers
    }

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        futures = [
            executor.submit(get_eligible_fcl_freight_rate_free_day, origin_detention_filters, freight_rates),
            executor.submit(get_eligible_fcl_freight_rate_free_day, destination_detention_filters, freight_rates),
            executor.submit(get_eligible_fcl_freight_rate_free_day, origin_demurrage_filters, freight_rates),
            executor.submit(get_eligible_fcl_freight_rate_free_day, destination_demurrage_filters, freight_rates),
        ]
        for i in range(0,len(futures)):
            results.append(futures[i].result())

    origin_detention_free_days = results[0]
    destination_detention_free_days = results[1]
    origin_demurrage_free_days = results[2]
    destination_demurrage_free_days = results[3]

    new_freight_rates = []
    for rate in freight_rates:
        rate["origin_detention"] = origin_detention_free_days[rate["id"]]
        rate["destination_detention"] = destination_detention_free_days[rate["id"]]
        rate["origin_demurrage"] = origin_demurrage_free_days[rate["id"]]
        rate["destination_demurrage"] = destination_demurrage_free_days[rate["id"]]
        rate["origin_plugin"] = None
        rate["destination_plugin"] = None
        new_freight_rates.append(rate)

    return new_freight_rates

def build_local_line_item_object(line_item, request):
    fcl_freight_local_charges = FCL_FREIGHT_LOCAL_CHARGES

    code_config = fcl_freight_local_charges[line_item['code']]

    is_additional_service = True if 'additional_service' in code_config.get('tags') else None
    if is_additional_service and line_item['code'] not in request['additional_services']:
        return None

    is_dpd = True if 'dpd' in code_config.get('tags') else False
    if is_dpd and ('import' in code_config.get('trade_types')) and (not request['include_destination_dpd']):
        return None

    slab_value = None

    if line_item.get('slabs'):
        if 'slab_containers_count' in code_config.get('tags'):
            slab_value = request['containers_count']

        if 'slab_cargo_weight_per_container' in code_config.get('tags'):
            slab_value = request['cargo_weight_per_container']

    if slab_value:
        slab = [t for t in line_item['slabs'] if (t['lower_limit'] <= slab_value) and (t['upper_limit'] >= slab_value)]
        if slab:
            slab=slab[0]
            line_item['price'] = slab['price']
            line_item['currency'] = slab['currency']
            
    line_item = {
        "code": line_item["code"],
        "unit": line_item["unit"],
        "price": line_item["price"],
        "currency": line_item["currency"],
        "remarks": line_item["remarks"] if 'remarks' in line_item else []
    }

    if line_item['unit'] == 'per_container':
        line_item['quantity'] = request['containers_count']
    elif line_item['unit'] == 'per_bl':
        line_item['quantity'] = request['bls_count']
    else:
        line_item['quantity'] = 1

    line_item['total_price'] = line_item['quantity'] * line_item['price']
    line_item['name'] = code_config.get('name')
    if is_dpd:
        line_item['is_dpd'] = is_dpd
    line_item['source'] = 'system'

    return line_item

def add_local_objects(freight_query_result, response_object, request):
    response_object['origin_local'] = {
        'id': freight_query_result['origin_local'].get('id'),
        'service_provider_id': freight_query_result['origin_local']['service_provider_id'] if freight_query_result['origin_local'].get('service_provider_id') else response_object['service_provider_id'],
        'source': freight_query_result['origin_local']['source'] if freight_query_result['origin_local'].get('source') else response_object['source'],
        'line_items': []
    } if 'origin_local' in freight_query_result and freight_query_result['origin_local'] else { 'line_items': [], 'service_provider_id': response_object['service_provider_id'], 'source':  response_object['source'] }

    response_object['destination_local'] = {}
    if freight_query_result.get('destination_local'):
        response_object['destination_local']['id'] =  freight_query_result['destination_local'].get('id')
        if freight_query_result['destination_local'].get('service_provider_id'):
            response_object['destination_local']['service_provider_id'] = freight_query_result['destination_local']['service_provider_id']
        else:
            response_object['destination_local']['service_provider_id'] = response_object['service_provider_id']

        if freight_query_result['destination_local'].get('source'):
            response_object['destination_local']['source'] = freight_query_result['destination_local']['source']
        else:
            response_object['destination_local']['source'] = response_object['source']
        response_object['destination_local']['line_items'] = []


    for line_item in ((freight_query_result.get('origin_local') or {}).get('line_items',[]) or []):
        if line_item.get('location_id'):
            if (line_item['location_id'] not in [request['destination_port_id'], request['destination_country_id']]):
                continue

        line_item = build_local_line_item_object(line_item, request)
        if not line_item:
            continue

        response_object['origin_local']['line_items'].append(line_item)

    for line_item in ((freight_query_result.get('destination_local') or {}).get('line_items',[]) or []):
        if line_item.get('location_id'):
            if (line_item['location_id'] not in [request['origin_port_id'], request['origin_country_id']]):
                continue

        line_item = build_local_line_item_object(line_item, request)

        if not line_item:
            continue

        response_object['destination_local']['line_items'].append(line_item)

    if len(list(set(request['additional_services']).difference([item['code'] for item in (response_object['origin_local']['line_items'] + response_object.get('destination_local').get('line_items',[]))]))) > 0:
        return False

    is_dpd_list = [t for t in response_object['destination_local'].get('line_items',[]) if t.get('is_dpd') == True]
    if len(is_dpd_list) > 0:
        is_dpd_list = is_dpd_list[0]
    else:
        is_dpd_list = []

    if request['include_destination_dpd'] and (not is_dpd_list):
        return False

    return True


def add_free_days_objects(freight_query_result, response_object, request):
    free_days_types = ['origin_detention', 'origin_demurrage', 'destination_detention', 'destination_demurrage']

    if request['container_type'] == 'refer':
        free_days_types += ['origin_plugin', 'destination_plugin']

    for free_days_type in free_days_types:
        if freight_query_result[free_days_type]:
            if not freight_query_result[free_days_type]['slabs']:
                freight_query_result[free_days_type]['slabs'] = []
            response_object[free_days_type] = freight_query_result[free_days_type] | {'unit': 'per_container'}
        else:
            response_object[free_days_type] = {'unit': 'per_container', "slabs": [] }

    return True

def add_weight_limit_object(freight_query_result, response_object, request):
    response_object['weight_limit'] = freight_query_result['weight_limit'] | {'unit': 'per_container'}
    return True

def build_additional_weight_line_item_object(additional_weight_rate, additional_weight_rate_currency, request):
    if not additional_weight_rate > 0:
        return

    line_item = OVERWEIGHT_SURCHARGE_LINE_ITEM

    line_item['price'] = additional_weight_rate
    line_item['currency'] = additional_weight_rate_currency

    if line_item['unit'] == 'per_container':
        line_item['quantity'] = request['containers_count']
    elif line_item['unit'] == 'per_bl':
        line_item['quantity'] = request['bls_count']
    else:
        line_item['quantity'] = 1
    line_item['total_price'] = line_item['quantity'] * line_item['price']
    line_item['source'] = 'system'

    return line_item

def build_freight_line_item_object(line_item, request):
    line_item = {
        "code": line_item["code"],
        "unit": line_item["unit"],
        "price": line_item["price"],
        "currency": line_item["currency"],
        "remarks": line_item["remarks"] if 'remarks' in line_item else []
    }

    fcl_freight_charges = FCL_FREIGHT_CHARGES

    code_config = fcl_freight_charges[line_item['code']]

    slab_value = None

    if line_item.get('slabs') and ('slab_containers_count' in code_config.get('tags')):
        slab_value = request['containers_count']

    if slab_value:
        slab = [t for t in line_item['slabs'] if t['lower_limit'] <= slab_value and t['upper_limit'] >= slab_value]
        if slab:
            slab = slab[0]
            line_item['price'] = slab['price']
            line_item['currency'] = slab['currency']

    if line_item['unit'] == 'per_container':
        line_item['quantity'] = request['containers_count']
    elif line_item['unit'] == 'per_bl':
        line_item['quantity'] = request['bls_count']
    else:
        line_item['quantity'] = 1

    line_item['total_price'] = line_item['quantity'] * line_item['price']
    line_item['name'] = code_config.get('name')
    line_item['source'] = 'system'

    return line_item

def build_freight_object(freight_validity, additional_weight_rate, additional_weight_rate_currency, request):
    freight_validity['validity_start'] = datetime.strptime(freight_validity['validity_start'],'%Y-%m-%d')
    freight_validity['validity_end'] = datetime.strptime(freight_validity['validity_end'],'%Y-%m-%d')

    if (freight_validity['validity_start'].date() > request['validity_end']) or (freight_validity['validity_end'].date() < request['validity_start']):
        return None

    freight_object = {
        'validity_start': freight_validity['validity_start'],
        'validity_end': freight_validity['validity_end'],
        'schedule_type': freight_validity['schedule_type'],
        'payment_term': freight_validity['payment_term'] or DEFAULT_PAYMENT_TERM,
        'validity_id': freight_validity['id'],
        'likes_count': freight_validity['likes_count'],
        'dislikes_count': freight_validity['dislikes_count'],
        'line_items': []
    }

    if freight_object['validity_start'].date() < request['validity_start']:
        freight_object['validity_start'] = request['validity_start']

    if freight_object['validity_end'].date() > request['validity_end']:
        freight_object['validity_end'] = request['validity_end']

    for line_item in freight_validity['line_items']:
        line_item = build_freight_line_item_object(line_item, request)

        if not line_item:
            continue

        freight_object['line_items'].append(line_item)

    overweight_surcharge = build_additional_weight_line_item_object(additional_weight_rate, additional_weight_rate_currency, request)
    if overweight_surcharge:
        freight_object['line_items'].append(overweight_surcharge)

    return freight_object

def add_freight_objects(freight_query_result, response_object, request):
    response_object['freights'] = []

    additional_weight_rate = 0
    additional_weight_rate_currency = 'USD'
    if request['cargo_weight_per_container'] and (request['cargo_weight_per_container'] - (response_object['weight_limit'].get('free_limit',0))) > 0:
        for slab in (response_object['weight_limit'].get('slabs',[]) or []):
            if slab['upper_limit'] < request['cargo_weight_per_container']:
                continue
            
            additional_weight_rate = slab['price']
            additional_weight_rate_currency = slab['currency']
            break

    freight_validities = freight_query_result['validities']

    for freight_validity in freight_validities:
      freight_object = build_freight_object(freight_validity, additional_weight_rate, additional_weight_rate_currency, request)
      if not freight_object:
        continue

      response_object['freights'].append(freight_object)


    return (len(response_object['freights']) > 0)



def build_response_object(freight_query_result, request):
    source = 'spot_rates'
    if freight_query_result['mode'] == 'predicted':
        source = 'predicted'
    elif freight_query_result['rate_type'] != 'market_place':
        source = freight_query_result['rate_type']
    response_object = {
      'shipping_line_id': freight_query_result['shipping_line_id'],
      'origin_port_id': freight_query_result['origin_port_id'],
      'destination_port_id': freight_query_result['destination_port_id'],
      'origin_country_id': freight_query_result['origin_country_id'],
      'destination_country_id': freight_query_result['destination_country_id'],
      'origin_main_port_id': freight_query_result['origin_main_port_id'],
      'destination_main_port_id': freight_query_result['destination_main_port_id'],
      'container_size': freight_query_result['container_size'],
      'container_type': freight_query_result['container_type'],
      'containers_count': request['containers_count'],
      'commodity': freight_query_result['commodity'],
      'service_provider_id': freight_query_result['service_provider_id'],
      'importer_exporter_id': freight_query_result['importer_exporter_id'],
      'source': source,
      'tags': [],
      'rate_id': freight_query_result['id']
    }

    if response_object['service_provider_id'] in CONFIRMED_INVENTORY['service_provider_ids']:
        response_object['tags'].append(CONFIRMED_INVENTORY['tag'])

    add_local_objects(freight_query_result, response_object, request)

    add_free_days_objects(freight_query_result, response_object, request)

    add_weight_limit_object(freight_query_result, response_object, request)

    add_freight_objects(freight_query_result, response_object, request)

    return response_object

def build_response_list(freight_rates, request):
    grouping = {}
    for freight_rate in freight_rates:
        # if freight_query_result['freight']['origin_main_port_id'] and freight_query_result['freight']['destination_main_port_id']:
        key = ':'.join([freight_rate['shipping_line_id'], freight_rate['service_provider_id'], freight_rate['origin_main_port_id'] or "", freight_rate['destination_main_port_id'] or "", freight_rate['rate_type'] or ""])
        if grouping.get(key) and grouping[key].get('importer_exporter_id'):
            continue
        response_object = build_response_object(freight_rate, request)

        if response_object:
            grouping[key] = response_object

    return list(grouping.values())


def discard_noneligible_lsps(freight_rates, requirements):
    ids = get_eligible_orgs('fcl_freight')

    freight_rates = [rate for rate in freight_rates if rate["service_provider_id"] in ids]
    return freight_rates

def discard_noneligible_shipping_lines(freight_rates, requirements):
    shipping_line_ids = [rate["shipping_line_id"] for rate in freight_rates]
    shipping_lines = get_shipping_line(id=shipping_line_ids)
    active_shipping_lines_ids = [sl["id"] for sl in shipping_lines if sl["status"] == "active"]
    freight_rates = [rate for rate in freight_rates if rate["shipping_line_id"] in active_shipping_lines_ids]
    return freight_rates

def discard_no_free_day_rates(freight_rates, requirements):
    rates = []
    for rate in freight_rates:
        if rate.get("destination_detention") and rate["destination_detention"].get("free_limit"):
            rates.append(rate)
        else:
            rate['destination_detention'] = {'free_limit':DEFAULT_FREE_DAY_LIMIT, 'slabs':[]}
            rates.append(rate)
    # freight_rates = [rate for rate in freight_rates if rate.get("destination_detention") and rate["destination_detention"].get("free_limit")]
    return rates

def discard_no_weight_limit_rates(freight_rates, requirements):
    if "cargo_weight_per_container" not in requirements:
        return freight_rates     
    
    new_freight_rates = []
    for rate in freight_rates:
        if ("weight_limit" not in rate) or ("free_limit" not in (rate.get("weight_limit") or {})) or (rate["weight_limit"]["free_limit"] < requirements["cargo_weight_per_container"] and ("slabs" not in rate["weight_limit"] or (not rate['weight_limit']['slabs']) or (rate["weight_limit"]["slabs"][-1] or {}).get("upper_limit") < requirements["cargo_weight_per_container"])):
            continue

        new_freight_rates.append(rate)

    return new_freight_rates

def pre_discard_noneligible_rates(freight_rates, requirements):
    if len(freight_rates) > 0:
        freight_rates = discard_noneligible_lsps(freight_rates, requirements)
    if len(freight_rates) > 0:
        freight_rates = discard_noneligible_shipping_lines(freight_rates, requirements)
    return freight_rates

def post_discard_noneligible_rates(freight_rates, requirements):
    freight_rates = discard_no_free_day_rates(freight_rates, requirements)
    # freight_rates = discard_no_weight_limit_rates(freight_rates, requirements)
    return freight_rates

def get_fcl_freight_rate_cards(requirements):
    """
    Returns all eligible rates according to requirements provided

    Response Format
        [{
            shipping_line_id:
            origin_main_port_id:
            destination_main_port_id:
            service_provider_id:
            source: 'spot_rates'
            origin_local: {
              service_provider_id
              source
              line_items: [{
                name:
                code:
                unit:
                quantity:
                price:
                total_price:
                currency:
                remarks:
              }],
            },
            destination_local: {
              service_provider_id
              source
              line_items: [{
                name:
                code:
                unit:
                quantity:
                price:
                total_price:
                currency:
                remarks:
              }]
            },
            origin_detention: {
              free_limit:
              slabs: [{
                lower_limit:
                upper_limit:
                price:
                currency:
              }]
              unit:
              remarks:
            },
            destination_detention: {
              free_limit:
              slabs: [{
                lower_limit:
                upper_limit:
                price:
                currency:
              }]
              unit:
              remarks:
            },
            origin_plugin: {
              free_limit:
              slabs: [{
                lower_limit:
                upper_limit:
                price:
                currency:
              }]
              unit:
              remarks:
            },
            destination_plugin: {
              free_limit:
              slabs: [{
                lower_limit:
                upper_limit:
                price:
                currency:
              }]
              unit:
              remarks:
            },
            destination_demurrage: {
              free_limit:
              slabs: [{
                lower_limit:
                upper_limit:
                price:
                currency:
              }]
              unit:
              remarks:
            },
            weight_limit: {
              free_limit:
              slabs: [{
                lower_limit:
                upper_limit:
                price:
                currency:
              }]
              unit:
              remarks:
            },
            freights: [{
              validity_start:
              validity_end:
              schedule_type:
              line_items: [{
                name:
                code:
                unit:
                quantity:
                price:
                total_price:
                currency:
                remarks:
              }],
            }]
        }]
    """
    try:
        initial_query = initialize_freight_query(requirements)
        freight_rates = jsonable_encoder(list(initial_query.dicts()))

        freight_rates = pre_discard_noneligible_rates(freight_rates, requirements)
        is_predicted = False

        if len(freight_rates) == 0:
            get_fcl_freight_predicted_rate(requirements)
            initial_query = initialize_freight_query(requirements, True)
            freight_rates = jsonable_encoder(list(initial_query.dicts()))
            is_predicted = True

        missing_local_rates = get_rates_which_need_locals(freight_rates)
        rates_need_destination_local = missing_local_rates["rates_need_destination_local"]
        rates_need_origin_local = missing_local_rates["rates_need_origin_local"]
        local_rates = get_missing_local_rates(requirements, rates_need_origin_local, rates_need_destination_local)
        freight_rates = fill_missing_locals_in_rates(freight_rates, local_rates)
        missing_free_weight_limit = get_rates_which_need_free_limit(requirements, freight_rates)

        if len(missing_free_weight_limit) > 0:
            free_weight_limits = get_missing_weight_limit(requirements, missing_free_weight_limit)
            freight_rates = fill_missing_weight_limit_in_rates(freight_rates, free_weight_limits, requirements)
        freight_rates = fill_missing_free_days_in_rates(requirements, freight_rates)
        freight_rates = post_discard_noneligible_rates(freight_rates, requirements)
        
        if is_predicted:
            fcl_freight_vyuh = FclFreightVyuh(freight_rates, requirements)
            freight_rates = fcl_freight_vyuh.apply_dynamic_pricing()
        
        freight_rates = build_response_list(freight_rates, requirements)
        return {
            "list" : freight_rates
        }
    except Exception as e:
        traceback.print_exc()
        sentry_sdk.capture_exception(e)
        print(e, 'Error In Fcl Freight Rate Cards')
        return {
            "list": []
        }