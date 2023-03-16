from services.fcl_freight_rate.interaction.get_fcl_freight_local_rate_cards import get_fcl_freight_local_rate_cards
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT, CONFIRMED_INVENTORY, PREDICTED_RATES_SERVICE_PROVIDER_IDS, DEFAULT_PAYMENT_TERM, INTERNAL_BOOKING, DEFAULT_SPECIFICITY_TYPE
from libs.dynamic_constants.fcl_freight_rate_dc import FclFreightRateDc
from datetime import datetime
from configs.fcl_freight_rate_constants import RATE_CONSTANT_MAPPING, OVERWEIGHT_SURCHARGE_LINE_ITEM, DEFAULT_EXPORT_DESTINATION_DETENTION, DEFAULT_IMPORT_DESTINATION_DETENTION, DEFAULT_EXPORT_DESTINATION_DEMURRAGE, DEFAULT_IMPORT_DESTINATION_DEMURRAGE, DEFAULT_LOCAL_AGENT_IDS
import concurrent.futures
from rails_client import client
from peewee import fn, JOIN
import yaml
from configs.defintions import FCL_FREIGHT_CHARGES,FCL_FREIGHT_LOCAL_CHARGES

def get_fcl_freight_rate_cards(request):
    freight_query = initialize_freight_query(request)
    freight_query = join_origin_local(freight_query)
    freight_query = join_destination_local(freight_query)

    freight_query = select_fields(freight_query)

    freight_query_result = freight_query_results(request, freight_query)

    lists = build_response_list(freight_query_result)

    lists = ignore_non_eligible_service_providers(lists)

    lists = ignore_non_active_shipping_lines(lists)

    if not lists and (request['commodity'] in ['sugar_rice', 'cotton_and_yarn', 'fabric_and_textiles', 'white_goods']):
        request['commodity'] = 'general'
        lists = get_fcl_freight_rate_cards(request)['list']
        lists = [{**x.pop('source', {}), 'source': 'predicted'} for x in lists]
        
    return {'list': lists}


def join_origin_local(freight_query):
    port_origin_locals = (FclFreightRateLocal.select(FclFreightRateLocal.id, FclFreightRateLocal.rate_not_available_entry, FclFreightRateLocal.is_line_items_error_messages_present, FclFreightRateLocal.data).alias('port_origin_locals'))
                
    freight_query = (freight_query
                     .join(port_origin_locals, JOIN.LEFT_OUTER, on=(port_origin_locals.c.id == FclFreightRate.origin_local_id))
                     .where(
                         (port_origin_locals.c.rate_not_available_entry.is_null(True)) | 
                         (port_origin_locals.c.rate_not_available_entry == False)
                     ))

    return freight_query


def join_destination_local(freight_query):
    port_destination_locals = (FclFreightRateLocal.select(FclFreightRateLocal.id, FclFreightRateLocal.rate_not_available_entry, FclFreightRateLocal.is_line_items_error_messages_present, FclFreightRateLocal.data).alias('port_destination_locals'))

    freight_query = (freight_query.
                     join(port_destination_locals, JOIN.LEFT_OUTER, on=(port_destination_locals.c.id == FclFreightRate.destination_local_id))
                     .where(
                         (port_destination_locals.c.rate_not_available_entry.is_null(True)) | 
                         (port_destination_locals.c.rate_not_available_entry == False)
                     ))

    return freight_query


def ignore_non_eligible_service_providers(lists):
    # ids = client.ruby.get_eligible_service_organizations({'service': 'fcl_freight'})['ids']
    ids = DEFAULT_LOCAL_AGENT_IDS['ids']

    result = [rate for rate in lists if rate['service_provider_id'] in ids]
    return result

def ignore_non_active_shipping_lines(lists):
    operator_result = client.ruby.list_operators({'filters':{'operator_type': 'shipping_line', 'status': 'active'}, 'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT, 'pagination_data_required':False})['list']
    ids = [item['id'] for item in operator_result]

    result = [rate for rate in lists if rate['shipping_line_id'] in ids]
    return result

def initialize_freight_query(request):
    rate_constant_mapping_key = request['cogo_entity_id']
    allow_entity_ids = [rate_mapping for rate_mapping in RATE_CONSTANT_MAPPING if rate_mapping['cogo_entity_id'] == rate_constant_mapping_key][0].get('allowed_entity_ids')

    freight_query = FclFreightRate.select().where(FclFreightRate.origin_port_id == request['origin_port_id'],FclFreightRate.destination_port_id == request['destination_port_id'],FclFreightRate.container_size == request['container_size'],FclFreightRate.container_type == request['container_type'],FclFreightRate.commodity == request['commodity'], FclFreightRate.cogo_entity_id.in_(allow_entity_ids), FclFreightRate.rate_not_available_entry == False, (FclFreightRate.importer_exporter_id == request['importer_exporter_id']) | (FclFreightRate.importer_exporter_id == None))
    freight_query = freight_query.where(FclFreightRate.last_rate_available_date >= request['validity_start'])

    if request['ignore_omp_dmp_sl_sps']:
        freight_query = freight_query.where(not (FclFreightRate.omp_dmp_sl_sp == request['ignore_omp_dmp_sl_sps']))
    return freight_query

def select_fields(freight_query):
    query_results = []

    # for q in freight_query.execute():
    #     result = {
    #         'freight':{
    #         'id':q.id,
    #         'validities' : q.validities,
    #         'container_size' : q.container_size,
    #         'container_type' : q.container_type,
    #         'commodity' : q.commodity,
    #         'origin_port_id' : q.origin_port_id,
    #         'destination_port_id' : q.destination_port_id,
    #         'origin_country_id' : q.origin_country_id,
    #         'destination_country_id' : q.destination_country_id,
    #         'origin_main_port_id' : q.origin_main_port_id,
    #         'destination_main_port_id' : q.destination_main_port_id,
    #         'importer_exporter_id' : q.importer_exporter_id,
    #         'service_provider_id' : q.service_provider_id,
    #         'shipping_line_id' : q.shipping_line_id,
    #         'weight_limit' : q.weight_limit,
    #         'origin_local' : q.origin_local,
    #         'destination_local' : q.destination_local,
    #         'is_origin_local_line_items_error_messages_present': q.is_origin_local_line_items_error_messages_present,
    #         'is_destination_local_line_items_error_messages_present': q.is_destination_local_line_items_error_messages_present,
    #         'cogo_entity_id': q.cogo_entity_id
    #     }}
    #     if q.origin_local_id:
    #         result = result | {'port_origin_local':{'line_items':q.origin_local_id.line_items['line_items'],'is_line_items_error_messages_present': q.origin_local_id.is_line_items_error_messages_present,'detention': q.origin_local_id.data['detention'],'demurrage': q.origin_local_id.data['demurrage'],'plugin': q.origin_local_id.data['plugin']}}

    #     if q.destination_local_id:
    #         result = result | {'port_destination_local':{'line_items': q.destination_local_id.data['line_items'],'is_line_items_error_messages_present' : q.destination_local_id.is_line_items_error_messages_present,'detention': q.destination_local_id.data['detention'],'demurrage': q.destination_local_id.data['demurrage'],'plugin': q.destination_local_id.data['plugin']}}

    #     query_results.append(result)            
    
    # # freight_query = freight_query.group_by(FclFreightRate.id)

    PortOriginLocals = FclFreightRateLocal.alias('port_origin_locals')
    PortDestinationLocals = FclFreightRateLocal.alias('port_destination_locals')

    freight_query = freight_query.select(
    fn.json_agg(
                fn.json_build_object(
                    'id', FclFreightRate.id,
                    'validities', FclFreightRate.validities,
                    'container_size', FclFreightRate.container_size,
                    'container_type', FclFreightRate.container_type,
                    'commodity', FclFreightRate.commodity,
                    'origin_port_id', FclFreightRate.origin_port_id,
                    'destination_port_id', FclFreightRate.destination_port_id,
                    'origin_country_id', FclFreightRate.origin_country_id,
                    'destination_country_id', FclFreightRate.destination_country_id,
                    'origin_main_port_id', FclFreightRate.origin_main_port_id,
                    'destination_main_port_id', FclFreightRate.destination_main_port_id,
                    'importer_exporter_id', FclFreightRate.importer_exporter_id,
                    'service_provider_id', FclFreightRate.service_provider_id,
                    'shipping_line_id', FclFreightRate.shipping_line_id,
                    'weight_limit', FclFreightRate.weight_limit,
                    'origin_local', FclFreightRate.origin_local,
                    'destination_local', FclFreightRate.destination_local,
                    'is_origin_local_line_items_error_messages_present',
                    FclFreightRate.is_origin_local_line_items_error_messages_present,
                    'is_destination_local_line_items_error_messages_present',
                    FclFreightRate.is_destination_local_line_items_error_messages_present
                )).alias("freight"),
        fn.json_agg(
            fn.json_build_object(
                'line_items', PortOriginLocals.data['line_items'],
                'is_line_items_error_messages_present', PortOriginLocals.is_line_items_error_messages_present,
                'plugin', PortOriginLocals.data["plugin"]
            )).alias("port_origin_local"),
        fn.json_agg(
            fn.json_build_object(
                'line_items', PortDestinationLocals.data["line_items"],
                'is_line_items_error_messages_present', PortDestinationLocals.is_line_items_error_messages_present,
                'plugin', PortDestinationLocals.data["plugin"]
            )).alias("port_destination_local")
        )
        
    freight_query = freight_query.group_by(FclFreightRate.id)
    return freight_query


def freight_query_results(request, freight_query):
    data = []

    origin_local_agent_service_rates = {}
    destination_local_agent_service_rates = {}

    if request['include_origin_local']:
        result_origin = get_fcl_freight_local_rate_cards({
        'trade_type': 'export',
        'country_id': request['origin_country_id'],
        'port_id': request['origin_port_id'],
        'container_size': request['container_size'],
        'container_type': request['container_type'],
        'commodity': request['commodity'],
        'containers_count': request['containers_count'],
        'bls_count': request['bls_count'],
        'cargo_weight_per_container': request['cargo_weight_per_container'],
        'rates':[],
        'service_provider_id' : None,
        'shipping_line_id' : None
        })['list']
    
        for t in result_origin:
            key = ':'.join([str(t['shipping_line_id']), str(t['main_port_id'])])
            origin_local_agent_service_rates[key] = t

    if request['include_destination_local']:
        result_destination = get_fcl_freight_local_rate_cards({
        'trade_type': 'import',  
        'country_id': request['origin_country_id'],
        'port_id': request['origin_port_id'],
        'container_size': request['container_size'],
        'container_type': request['container_type'],
        'commodity': request['commodity'],
        'containers_count': request['containers_count'],
        'bls_count': request['bls_count'],
        'cargo_weight_per_container': request['cargo_weight_per_container'],
        'rates':[],
        'service_provider_id' : None,
        'shipping_line_id' : None
        })['list']
    
        for t in result_destination:
            key = ':'.join([str(t['shipping_line_id']), str(t['main_port_id'])])
            destination_local_agent_service_rates[key] = t

    origin_default_local_agent_service_rates = {k: v for k, v in origin_local_agent_service_rates.items() if v['service_provider_id'] == FclFreightRateDc.get_key_value('DEFAULT_LOCAL_AGENT_ID')}
    destination_default_local_agent_service_rates = {k: v for k, v in destination_local_agent_service_rates.items() if v['service_provider_id'] == FclFreightRateDc.get_key_value('DEFAULT_LOCAL_AGENT_ID')}

    origin_local_agent_service_rates = {k: v for k, v in origin_local_agent_service_rates.items() if v['service_provider_id'] != FclFreightRateDc.get_key_value('DEFAULT_LOCAL_AGENT_ID')}
    destination_local_agent_service_rates = {k: v for k, v in destination_local_agent_service_rates.items() if v['service_provider_id'] != FclFreightRateDc.get_key_value('DEFAULT_LOCAL_AGENT_ID')}

    for query in freight_query.execute():
        result = {}
        result['freight'] = query.freight[0] if query.freight else {}
        result['port_origin_local'] = query.port_origin_local[0] if query.port_origin_local else {}
        result['port_destination_local'] = query.port_destination_local[0] if query.port_destination_local else {}

        result['weight_limit'] = result['freight']['weight_limit']

        if (not result['weight_limit'].get('free_limit')) or (not result['weight_limit'].get('slabs')):
            fcl_weight_slabs = get_default_overweight_surcharges(result, request)

            if fcl_weight_slabs:
                result['weight_limit']['free_limit'] = fcl_weight_slabs['max_weight']
                if fcl_weight_slabs['slabs']:
                    result['weight_limit']['slabs'] = fcl_weight_slabs['slabs'] 

    
        # result['origin_detention'] = result['freight']['origin_local'].get('detention') or result['port_origin_local'].get('detention')
        # result['destination_detention'] = result['freight']['destination_local'].get('detention') or result['port_destination_local'].get('detention')

        result['origin_plugin'] = {}
        result['destination_plugin'] = {}

        if request['container_type'] == 'refer':
            result['origin_plugin'] = (result['freight']['origin_local'].get('plugin') or result['port_origin_local']['plugin'])
            result['destination_plugin'] = (result['freight']['destination_local'].get('plugin') or result['port_destination_local']['plugin'])
        
        # result['origin_demurrage'] = {}
        # result['destination_demurrage'] = (result['freight']['destination_local'].get('demurrage') or result['port_destination_local']['demurrage'])

        result['origin_local'] = {}
        result['origin_local_service_provider'] = []
        result['destination_local_service_provider'] = []

        if request['include_origin_local']:
            if result['freight']['is_origin_local_line_items_error_messages_present'] == False:
                result['origin_local'] = result['freight']['origin_local'] 
            if not result['origin_local'] and result['port_origin_local'].get('is_line_items_error_messages_present') == False:
                result['origin_local'] = result['port_origin_local'] 

            result['origin_local'] = origin_local_agent_service_rates.get(':'.join([str(result['freight']['shipping_line_id']), str(result['freight']['origin_main_port_id'])])) if not result['origin_local'] else {}
            result['origin_local'] = origin_default_local_agent_service_rates.get(':'.join([str(result['freight']['shipping_line_id']), str(result['freight']['origin_main_port_id'])])) if not result['origin_local'] else {}
            if result['origin_local']["service_provider_id"]:
                result['origin_local_service_provider'].append(result['origin_local']["service_provider_id"]) 
     
        result['destination_local'] = {}
        if request['include_destination_local']:
            if result['freight']['is_destination_local_line_items_error_messages_present'] == False:
                result['destination_local'] = result['freight']['destination_local']
            if not (result['destination_local']) and result['port_destination_local']['is_line_items_error_messages_present'] == False:
                result['destination_local'] = result['port_destination_local']
        
            result['destination_local'] = destination_local_agent_service_rates.get(':'.join([str(result['freight']['shipping_line_id']), str(result['freight']['destination_main_port_id'])])) if not result['destination_local'] else {}
            result['destination_local'] = destination_default_local_agent_service_rates.get(':'.join([str(result['freight']['shipping_line_id']), str(result['freight']['destination_main_port_id'])])) if not result['destination_local'] else {}
            if result['destination_local']["service_provider_id"]:
                result['destination_local_service_provider'].append(result['destination_local']["service_provider_id"]) 
        
        # if result['origin_detention'] and result['origin_demurrage'] and result['destination_demurrage'] and result['destination_detention']:
        #     if (not result['origin_detention'].get('free_limit')) or (not result['destination_detention'].get('free_limit')) or (not result['origin_demurrage'].get('free_limit')) or (not result['destination_demurrage'].get('free_limit')):
        #         result = get_eligible_detention_and_demurrage_free_days(result, request)
        
        result['origin_detention'] = {}
        result['destination_detention'] = {}
        result['origin_demurrage'] = {}
        result['destination_demurrage'] = {}

        result = get_eligible_detention_and_demurrage_free_days(result)

        if not result['destination_detention'].get('free_limit'):
            continue

        data.append(result)
        return data

def build_response_list(freight_query_results):
    grouping = {}

    for freight_query_result in freight_query_results:
        if freight_query_result['freight']['origin_main_port_id'] and freight_query_result['freight']['destination_main_port_id']:
            key = ':'.join([freight_query_result['freight']['shipping_line_id'], freight_query_result['freight']['service_provider_id'], freight_query_result['freight']['origin_main_port_id'], freight_query_result['freight']['destination_main_port_id']])
            if grouping.get(key) and grouping[key].get('importer_exporter_id'):
                continue
            response_object = build_response_object(freight_query_result)
        
            if response_object:
                grouping[key] = response_object 

    return grouping.values()

def build_response_object(freight_query_result, request):
    response_object = {
      'shipping_line_id': freight_query_result['freight']['shipping_line_id'],
      'origin_port_id': freight_query_result['freight']['origin_port_id'],
      'destination_port_id': freight_query_result['freight']['destination_port_id'],
      'origin_country_id': freight_query_result['freight']['origin_country_id'],
      'destination_country_id': freight_query_result['freight']['destination_country_id'],
      'origin_main_port_id': freight_query_result['freight']['origin_main_port_id'],
      'destination_main_port_id': freight_query_result['freight']['destination_main_port_id'],
      'container_size': freight_query_result['freight']['container_size'],
      'container_type': freight_query_result['freight']['container_type'],
      'containers_count': request['containers_count'],
      'commodity': freight_query_result['freight']['commodity'],
      'service_provider_id': freight_query_result['freight']['service_provider_id'],
      'importer_exporter_id': freight_query_result['freight']['importer_exporter_id'],
      'source': 'predicted' if (freight_query_result['freight']['service_provider_id'] in PREDICTED_RATES_SERVICE_PROVIDER_IDS) else 'spot_rates',
      'tags': [],
      'rate_id': freight_query_result['freight']['id']
    }
    
    if response_object['service_provider_id'] in CONFIRMED_INVENTORY['service_provider_ids']:
        response_object['tags'].append(CONFIRMED_INVENTORY['tag'])

    if not add_local_objects(freight_query_result, response_object, request):
        return None

    if not add_free_days_objects(freight_query_result, response_object, request):
        return None
    
    if not add_weight_limit_object(freight_query_result, response_object):
        return None
        
    if not add_freight_objects(freight_query_result, response_object):
        return None

    return response_object

def add_local_objects(freight_query_result, response_object,request):
    response_object['origin_local'] = {
        'service_provider_id': freight_query_result['origin_local']['service_provider_id'] if freight_query_result['origin_local']['service_provider_id'] else response_object['service_provider_id'],
        'source': freight_query_result['origin_local']['source'] if freight_query_result['origin_local']['source'] else response_object['source'],
        'line_items': []
    }
    response_object['destination_local'] = {
      'service_provider_id': freight_query_result['destination_local']['service_provider_id'] if freight_query_result['destination_local']['service_provider_id'] else response_object['service_provider_id'],
      'source': freight_query_result['destination_local']['source'] if freight_query_result['destination_local']['soruce'] else response_object['source'],
      'line_items': []
    }
    
    for line_item in freight_query_result['origin_local'].get('line_items'):
        if (line_item['location_id']) and (line_item['location_id'] not in [request['destination_port_id'], request['destination_country_id']]):
            continue

        line_item = build_local_line_item_object(line_item)
        if not line_item:
            continue

        response_object['origin_local']['line_items'].append(line_item)
    
    for line_item in freight_query_result['destination_local'].get('line_items'):
        if line_item['location_id'] and (line_item['location_id'] not in [request['origin_port_id'], request['origin_country_id']]):
            continue

        line_item = build_local_line_item_object(line_item)

        if not line_item:
            continue

        response_object['destination_local']['line_items'].append(line_item)

    if list(set(request['additional_services']).difference([item['code'] for item in (response_object['origin_local']['line_items'] + response_object['destination_local']['line_items'])])).count > 0:
        return False

    if request['include_destination_dpd'] and (not [t for t in response_object['destination_local']['line_items'] if t['is_dpd'] == True][0]):
        return False

    return True


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

    if line_item['slabs']:
        if 'slab_containers_count' in code_config.get('tags'):
            slab_value = request['containers_count']

        if 'slab_cargo_weight_per_container' in code_config.get('tags'):
            slab_value = request['cargo_weight_per_container']

    if slab_value:
        slab = [t for t in line_item['slabs'] if (t['lower_limit'] <= slab_value) and (t['upper_limit'] >= slab_value)][0]
        if slab:
            line_item['price'] = slab['price']
            line_item['currency'] = slab['currency']
    
    line_item = {key: line_item[key] for key in ['code', 'unit', 'price', 'currency', 'remarks']}
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

def add_free_days_objects(freight_query_result, response_object, request):
    free_days_types = ['origin_detention', 'origin_demurrage', 'destination_detention', 'destination_demurrage']

    if request['container_type'] == 'refer': 
        free_days_types += ['origin_plugin', 'destination_plugin']

    for free_days_type in free_days_types:
        response_object[free_days_type] = freight_query_result[free_days_type] | {'unit': 'per_container'}

    return True

def add_weight_limit_object(freight_query_result, response_object, request):
    response_object['weight_limit'] = freight_query_result['weight_limit'] | {'unit': 'per_container'}
    
    if not request['cargo_weight_per_container']:
        return True 

    if not response_object['weight_limit']['free_limit']:
        return True

    if request['cargo_weight_per_container'] <= response_object['weight_limit']['free_limit']:
        return True

    if not response_object['weight_limit']['slabs'][-1]:
        return False

    if request['cargo_weight_per_container'] > (response_object['weight_limit']['free_limit'] + response_object['weight_limit']['slabs'])[-1]['upper_limit']:
        return False

    return True

def add_freight_objects(freight_query_result, response_object,request):
    response_object['freights'] = []

    additional_weight_rate = 0
    additional_weight_rate_currency = 'USD'

    if request['cargo_weight_per_container'] and (request['cargo_weight_per_container'] - response_object['weight_limit']['free_limit']) > 0:
        for slab in response_object['weight_limit']['slabs']:
            if slab['upper_limit'] < request['cargo_weight_per_container']:
                continue

            additional_weight_rate = slab['price']
            additional_weight_rate_currency = slab['currency']
            break

    freight_validities = freight_query_result['freight']['validities']
    
    for freight_validity in freight_validities:
      freight_object = build_freight_object(freight_validity, additional_weight_rate, additional_weight_rate_currency)
      if not freight_object:
        continue

      response_object['freights'].append(freight_object)


    return (response_object['freights'].count > 0)

def build_freight_object(freight_validity, additional_weight_rate, additional_weight_rate_currency, request):
    freight_validity['validity_start'] = datetime.strptime(freight_validity['validity_start'],'%Y-%m-%d')
    freight_validity['validity_end'] = datetime.strptime(freight_validity['validity_end'],'%Y-%m-%d')

    if (freight_validity['validity_start'] > request['validity_end']) or (freight_validity['validity_end'] < request['validity_start']):
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

    if freight_object['validity_start'] < datetime.strptime(request['validity_start'],'%Y-%m-%d'):
        freight_object['validity_start'] = request['validity_start'] 
    
    if freight_object['validity_end'] > datetime.strptime(request['validity_end'],'%Y-%m-%d'):
        freight_object['validity_end'] = request['validity_end'] 
    
    for line_item in freight_validity['line_items']:
        line_item = build_freight_line_item_object(line_item, additional_weight_rate, additional_weight_rate_currency, request)

        if not line_item:
            continue

        freight_object['line_items'].append(line_item)

    overweight_surcharge = build_additional_weight_line_item_object(additional_weight_rate, additional_weight_rate_currency)
    if overweight_surcharge:
        freight_object['line_items'].append(overweight_surcharge) 

    return freight_object

def build_freight_line_item_object(line_item, request):
    line_item = {key: line_item[key] for key in ['code', 'unit', 'price', 'currency', 'remarks']}
    
    fcl_freight_charges = FCL_FREIGHT_CHARGES

    code_config = fcl_freight_charges[line_item['code']]

    slab_value = None

    if line_item['slabs'] and ('slab_containers_count' in code_config.get('tags')):
        slab_value = request['containers_count']

    if slab_value:
        slab = [t for t in line_item['slabs'] if t['lower_limit'] <= slab_value and t['upper_limit'] >= slab_value][0]
        if slab:
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


def build_additional_weight_line_item_object(additional_weight_rate, additional_weight_rate_currency,request):
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

# def ignore_internal_service_providers(list):
#     internal_service_provider_ids = [INTERNAL_BOOKING['service_provider_id']]
    
#     rates = [rate for rate in list if rate['service_provider_id'] not in internal_service_provider_ids]
#     shipping_line_ids = [rate['shipping_line_id'] for rate in rates]
    
#     internal_rates = [rate for rate in list if rate['service_provider_id'] in internal_service_provider_ids]
#     internal_rates = [rate for rate in internal_rates if rate['shipping_line_id'] not in shipping_line_ids]


#     return (rates + internal_rates)

# def ignore_confirmed_inventory_rates(list, request): 
#     if request['include_confirmed_inventory_rates'] == True:
#         return list
    
#     rates = [rate for rate in list if rate['tags'] not in CONFIRMED_INVENTORY['tag']]
#     return rates


def get_default_overweight_surcharges(result, request):
    organization_category = client.ruby.get_organization({'id': result['freight']['service_provider_id']})['data']['category_types']

    weight_slab_result = client.ruby.get_fcl_weight_slabs_configuration({
        'filters': {
            'origin_location_id': [request['origin_port_id'], request['origin_country_id']], 
            'destination_location_id': [request['destination_port_id'], request['destination_country_id']], 
            'origin_location_type': ['seaport', 'country'], 
            'destination_location_type': ['seaport', 'country'], 
            'organization_category': organization_category,
            'shipping_line_id': [result['freight']['shipping_line_id']], 
            'service_provider_id': [result['freight']['service_provider_id']], 
            'importer_exporter_id': [request['importer_exporter_id']], 
            'is_cogo_assured': [False], 
            'container_size': [request['container_size']], 
            'commodity': [request['commodity']]
            }
        })
    return weight_slab_result 

def get_eligible_detention_and_demurrage_free_days(result,request):
    detention_and_demurrage_free_days = []

    common_filters = {
      'container_size': result['freight']['container_size'],
      'container_type': result['freight']['container_type'],
      'shipping_line_id': result['freight']['shipping_line_id'],
      'service_provider_id': result['freight']['service_provider_id'],
      'importer_exporter_id': result['freight']['importer_exporter_id'],
    #   'specificity_type': DEFAULT_SPECIFICITY_TYPE
       'validity_start': result['validity_start'],
       'validity_end': result['validity_end']
    }

    # if result['origin_detention']:
    #     if not result['origin_detention'].get('free_limit'):
    #         detention_and_demurrage_free_days.append({
    #             'filters': {'location_id': [request['origin_port_id'], request['origin_country_id']], 'trade_type': 'export','free_days_type': 'detention'} | common_filters, 
    #             'interaction': 'origin_detention'
    #         })
    origin_local_service_providers =  list(set(result['origin_local_service_provider']))

    # if result['origin_demurrage']:
    #     if not result['origin_demurrage'].get('free_limit'):
    #         detention_and_demurrage_free_days.append({
    #             'filters': {'location_id': [request['origin_port_id'], request['origin_country_id']], 'trade_type': 'export', 'free_days_type': 'demurrage'} | common_filters,
    #             'interaction': 'origin_demurrage'
    #     })
    destination_local_service_providers = list(set(result['destination_local_service_provider']))

    # if result['destination_detention']:
    #     if not result['destination_detention'].get('free_limit'):
    #         detention_and_demurrage_free_days.append({
    #             'filters': {'location_id': [request['destination_port_id'], request['destination_country_id']], 'trade_type': 'import', 'free_days_type': 'detention' } | common_filters,
    #             'interaction': 'destination_detention'
    #     })
    detention_and_demurrage_free_days.append({
       'filters': { 'location_id': [request['origin_port_id'], request['origin_country_id']], 'trade_type': 'export', 'free_days_type': 'demurrage', 'local_service_provider_ids': origin_local_service_providers } | (common_filters),
       'interaction': 'origin_detention'
     })    
    # if result['destination_demurrage']:
    #     if not result['destination_demurrage'].get('free_limit'):
    #         detention_and_demurrage_free_days.append({
    #             'filters': {'location_id': [request['destination_port_id'], request['destination_country_id']], 'trade_type': 'import', 'free_days_type': 'demurrage'} | common_filters,
    #             'interaction': 'destination_demurrage'
    #     })

    detention_and_demurrage_free_days.append({
       'filters': { 'location_id': [request['origin_port_id'], request['origin_country_id']], 'trade_type': 'export', 'free_days_type': 'demurrage', 'local_service_provider_ids': origin_local_service_providers } | (common_filters),
       'interaction': 'origin_demurrage'
     })

    detention_and_demurrage_free_days.append({
       'filters': { 'location_id': [request['destination_port_id'], request['destination_country_id']], 'trade_type': 'import', 'free_days_type': 'detention', 'local_service_provider_ids': destination_local_service_providers } | (common_filters),
       'interaction': 'destination_detention'
     })
    
    detention_and_demurrage_free_days.append({
       'filters': { 'location_id': [request['destination_port_id'], request['destination_country_id']], 'trade_type': 'import', 'free_days_type': 'demurrage', 'local_service_provider_ids': destination_local_service_providers } | (common_filters),
       'interaction': 'destination_demurrage'
     })
    
    with concurrent.futures.ThreadPoolExecutor(max_workers = len(detention_and_demurrage_free_days)) as executor:
        futures = [executor.submit(get_eligible_fcl_freight_rate_free_day, free_day) for free_day in detention_and_demurrage_free_days]
        method_responses = {}
        for future in futures:
            result = future.result()
            method_responses.update(result)

    required_attributes = ['free_limit', 'slabs', 'remarks', 'previous_days_applicable', 'specificity_type', 'validity_start', 'validity_end']

    # if not (result['origin_detention'].get('free_limit')) and method_responses['origin_detention']:
    if method_responses['origin_detention']:
        result['origin_detention'] = {k: method_responses['origin_detention'][k] for k in required_attributes if k in method_responses['origin_detention']}
    else:
        result['origin_detention'] = { 'free_limit' : FclFreightRateDc.get_key_value('FREE_DAY_DEFAULT_ORIGIN_DETENTION') }


    # if (not result['origin_demurrage'].get('free_limit')) and method_responses['origin_demurrage']:
    if method_responses['origin_demurrage']:
        result['origin_demurrage'] = {k: method_responses['origin_demurrage'][k] for k in required_attributes if k in method_responses['origin_demurrage']}
    else:
       result['origin_demurrage'] = {'free_limit' : FclFreightRateDc.get_key_value('FREE_DAY_DEFAULT_ORIGIN_DEMURRAGE')}
    

    # if not result['destination_detention'].get('free_limit'):
    #     if method_responses['destination_detention']:
    #         result['destination_detention'] = {k: method_responses['destination_detention'][k] for k in required_attributes if k in method_responses['destination_detention']}
    #     else:
    #         result['destination_detention'] = {'free_limit':eval("DEFAULT_{}_DESTINATION_DETENTION".format(request['trade_type'].upper()))}
    if method_responses['destination_detention']:
       result['destination_detention'] = {key:value for key,value in method_responses['destination_detention'].items() if key in required_attributes}
    else:
       result['destination_detention'] = {'free_limit' : FclFreightRateDc.get_key_value('FREE_DAY_DEFAULT_DESTINATION_DETENTION') }
    

    # if not result['destination_demurrage'].get('free_limit'):
    #     if method_responses['destination_demurrage']:
    #         result['destination_demurrage'] = {k: method_responses['destination_demurrage'][k] for k in required_attributes if k in method_responses['destination_demurrage']}
    #     else:
    #         result['destination_demurrage'] = {'free_limit':eval("DEFAULT_{}_DESTINATION_DEMURRAGE".format(request['trade_type'].upper()))} 
    
    if method_responses['destination_demurrage']:
       result['destination_demurrage'] = {key:value for key,value in method_responses['destination_demurrage'].items() if key in required_attributes}
    else:
       result['destination_demurrage'] = {'free_limit' : FclFreightRateDc.get_key_value('FREE_DAY_DEFAULT_DESTINATION_DEMURRAGE')}
    
    return result

def get_eligible_fcl_freight_rate_free_day(free_day):
    data = client.ruby.get_eligible_fcl_freight_rate_free_day({'filters':{free_day['filters']}}) 

    return data['interaction']