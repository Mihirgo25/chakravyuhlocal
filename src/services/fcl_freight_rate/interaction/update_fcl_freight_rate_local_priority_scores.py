from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
import concurrent.futures
from datetime import datetime, timedelta
import pytz
from operator import attrgetter
from micro_services.client import *
from configs.global_constants import POTENTIAL_CONTAINERS_BOOKING_COUNTS, POTENTIAL_CONVERSION_RATIO
from database.db_session import db
from database.rails_db import *

possible_direct_filters = ['id', 'port_id', 'main_port_id', 'trade_type', 'container_size', 'container_type', 'commodity', 'shipping_line_id']

def update_fcl_freight_rate_local_priority_scores_data(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            raise e

def execute_transaction_code(request):
    request = request.__dict__
    request['filters'] = {key: value for key, value in request['filters'].items() if not value.empty() and possible_direct_filters.include(key)}
    groups = get_groupings(request)
    for group in groups:
        with concurrent.futures.ThreadPoolExecutor() as executor: 
            update_priority_score(group)

def get_groupings(request):
    groups = FclFreightRateLocal.select(FclFreightRateLocal.port_id, FclFreightRateLocal.main_port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id)
    for filter in request['filters']:
        groups = groups.select().where(attrgetter(filter)(FclFreightRateLocal) == request['filters'][filter])
    groups = [ {k:v for k,v in t.items() if k != 'id'} for t in groups ]
    return groups

def update_priority_score(group):
    spot_searches = SpotSearchFclFreightService.select().where('created_at' > datetime.now(pytz.utc) - timedelta(days=30) and 'selected_shipping_line_id' == set(group['shipping_line_id'], None))
    if group['trade_type'] == 'export':
        spot_searches.select().where('origin_port_id' == group['port_id'])
    else:
        spot_searches.select().where('destination_port_id' == group['port_id'])
    spot_search_ids = spot_searches.select(spot_searches.spot_search_id).execute()
    spot_searches = common.list_spot_searches({'filters':{'id':spot_search_ids}})
    importer_exporter_ids = set(spot_searches.select(spot_searches.importer_exporter_id).execute())
    spot_searches_importer_exporters_count = importer_exporter_ids.count()
    organization_sizes = organization.list_organizations({'pagination_data_required': False, 'filters': { 'id': importer_exporter_ids }, 'page_limit': 1000 })['list']
    res = {}
    for i, v in organization_sizes['sizes'].items():
        res[v] = [i] if v not in res.keys() else res[v] + [i]

    organization_sizes = res
    containers_from_spot_searches = 0

    for k,v in organization_sizes:
        containers_from_spot_searches += POTENTIAL_CONTAINERS_BOOKING_COUNTS[k] * v.count()

    fcl_bookings = ShipmentFclFreightService.select().where('created_at' > datetime.now(pytz.utc) - timedelta(days=30))

    if group['trade_type'] == 'export':
        fcl_bookings.select().where('origin_port_id' == group['port_id'] and 'orgin_main_port_id' == group['main_port_id'])
    else:
        fcl_bookings.select().where('destination_port_id' == group['port_id'] and 'destination_main_port_id' == group['main_port_id'])
    
    booking_ids = fcl_bookings.select(fcl_bookings.shipment_id).execute()
    bookings_importer_exporters_count = set(Shipment.select(Shipment.importer_exporter_id).where(id == booking_ids).execute()).count()
    containers_count_list = fcl_bookings.select(fcl_bookings.containers_count).execute()
    containers_from_bookings = 0
    for i in containers_count_list:
        containers_from_bookings += i

    containers_count = [containers_from_spot_searches * POTENTIAL_CONVERSION_RATIO, containers_from_bookings].max()
    importer_exporters_count = [spot_searches_importer_exporters_count * POTENTIAL_CONVERSION_RATIO, bookings_importer_exporters_count].max()

    score = ([containers_count, 1000].min() / 10)

    FclFreightRateLocal.where(group).update('containers_count' == containers_count).execute()
    FclFreightRateLocal.where(group).update('importer_exporters_count' == importer_exporters_count).execute()
    FclFreightRateLocal.where(group).update('priority_score' == int(score)).execute()
    FclFreightRateLocal.where(group).update('priority_score_updated_at' == datetime.now(pytz.utc)).execute()