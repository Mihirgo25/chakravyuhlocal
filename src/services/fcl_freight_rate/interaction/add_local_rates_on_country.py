from configs.global_constants import HAZ_CLASSES
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID, DEFAULT_SHIPPING_LINE_ID
from configs.env import DEFAULT_USER_ID
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from micro_services.client import maps
import concurrent.futures

def add_local_rates_on_country(request):
    ports_data = get_ports_of_country(request.get('country_id') , BATCH_SIZE = 50)
    icd_ports, combined_ids = [], []
    for data in ports_data:
        if data.get('is_icd') == True:
            icd_ports.append(str(data.get('id')))
        elif data.get('is_icd') == False:
            combined_ids.append(str(data.get('id')) + ':')

    main_ports_icd_mapping = maps.list_locations_mapping({'location_id':icd_ports,'type':['main_ports']})
    if isinstance(main_ports_icd_mapping, dict) and main_ports_icd_mapping.get('list'):
        main_ports_data = main_ports_icd_mapping['list']
    else:
        main_ports_data = []

    for port in main_ports_data:
        combined_ids.append(str(port['icd_port_id'])+':'+str(port['id']))

    query_result = get_search_query(request)
    mapping_from_query = [str(row['port_id'])+':'+str(row['main_port_id'] or '') for row in query_result]
    final_list = list(set(combined_ids).difference(set(mapping_from_query)))
    if final_list:
        get_params_and_create_local(request, final_list)


def get_params_and_create_local(request, final_list):
    final_params = []

    local_freight_param = {
        'trade_type': request.get('trade_type'), 
        'container_size': request.get('container_size'),
        'container_type': request.get('container_type'),
        'commodity': request.get('commodity') if request.get('commodity') in HAZ_CLASSES else None,
        'service_provider_id': request['service_provider_id'] if request.get('service_provider_id') else DEFAULT_SERVICE_PROVIDER_ID,
        'performed_by_id': request['performed_by_id'] if request.get('performed_by_id') else DEFAULT_USER_ID,
        'procured_by_id': request['procured_by_id'] if request.get('procured_by_id') else DEFAULT_USER_ID,
        'sourced_by_id': request['sourced_by_id'] if request.get('sourced_by_id') else DEFAULT_USER_ID,
        'shipping_line_id' : request.get('shipping_line_id') if request.get('shipping_line_id') else DEFAULT_SHIPPING_LINE_ID
    }

    for port in final_list:
        port_id, main_port_id = port.split(':')
        creation_param = local_freight_param | {'port_id': port_id, 'data':request.get('data')}
        if main_port_id:
            creation_param['main_port_id'] = main_port_id
        else:
            creation_param['main_port_id'] = None
      
        final_params.append(creation_param)

    with concurrent.futures.ThreadPoolExecutor(max_workers = len(final_params)) as executor:
        futures = [executor.submit(create_fcl_freight_rate_local, param) for param in final_params]

def get_search_query(local_rate_param):
    query = FclFreightRateLocal.select().where(
    FclFreightRateLocal.country_id == local_rate_param.get('country_id'),
    FclFreightRateLocal.trade_type == local_rate_param.get('trade_type'),
    FclFreightRateLocal.container_size == local_rate_param.get('container_size'),
    FclFreightRateLocal.container_type == local_rate_param.get("container_type"),
    ((FclFreightRateLocal.commodity == local_rate_param.get('commodity')) | (FclFreightRateLocal.commodity.is_null(True)))
    )

    if local_rate_param.get('shipping_line_id'):
        query = query.where(FclFreightRateLocal.shipping_line_id == local_rate_param['shipping_line_id'])
    return list(query.dicts())

def get_ports_of_country(location_id, BATCH_SIZE):
    locations_data = []
    for page_no in range(1,BATCH_SIZE):
        locations = maps.list_locations({'filters':{'country_id': location_id, 'status':'active', "type":"seaport"},'page':page_no, 'page_limit':BATCH_SIZE})['list']
        locations_data.extend(locations)
        if len(locations) < BATCH_SIZE:
            break

    return locations_data