from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import concurrent.futures
from datetime import datetime, timedelta
import pytz
from configs.global_constants import POTENTIAL_CONTAINERS_BOOKING_COUNTS, POTENTIAL_CONVERSION_RATIO
from database.db_session import db
from micro_services.client import *
from database.rails_db import *

possible_direct_filters = ['id', 'origin_port_id', 'destination_port_id', 'origin_main_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'importer_exporter_id']

def update_fcl_freight_rate_priority_scores_data(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            raise e

def execute_transaction_code(request):
    request = request.__dict__
    request['filters'] = {key: value for key, value in request['filters'] if not value.empty() and possible_direct_filters.include(key)}
    groups = get_groupings(request)
    for group in groups:
        with concurrent.futures.ThreadPoolExecutor() as executor: 
            update_priority_score(group)

def get_groupings(request):
    groups = FclFreightRate.select(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.shipping_line_id, FclFreightRate.importer_exporter_id).where(request['filters']).execute()
    groups = [ {k:v for k,v in t.items() if k != 'id'} for t in groups ]
    return groups

def update_priority_score(group):
    spot_search_ids = SpotSearchFclFreightService.select(SpotSearchFclFreightService.spot_search_id).where('created_at' > datetime.now(pytz.utc) - timedelta(days=30) and 'origin_port_id' == group['origin_port_id'] and 'destination_port_id' == group['destination_port_id'] and 'container_size' == group['container_size'] and 'container_type' == group['container_type'] and 'commodity' == group['commodity']).execute()
    spot_searches = common.list_spot_searches({'filters':{'id' : spot_search_ids}})

    if group['importer_exporter_id']:
        spot_searches = spot_searches.select().where('importer_exporter_id' == group['importer_exporter_id'])

    importer_exporter_ids = set(spot_searches.select('importer_exporter_id').execute())
    spot_searches_importer_exporters_count = importer_exporter_ids.count()

    organization_sizes = get_service_provider(importer_exporter_ids)
    res = {}
    for i, v in organization_sizes.get('sizes').items():
        res[v] = [i] if v not in res.keys() else res[v] + [i]

    organization_sizes = res
    containers_from_spot_searches = 0

    for k,v in organization_sizes:
        containers_from_spot_searches += POTENTIAL_CONTAINERS_BOOKING_COUNTS[k] * v.count()

    booking_ids = ShipmentFclFreightService.select(ShipmentFclFreightService.shipment_id).where('created_at' > datetime.now(pytz.utc) - timedelta(days=30) and 'origin_port_id' == group['origin_port_id'] and 'destination_port_id' == group['destination_port_id'] and 'origin_main_port_id' == group['origin_main_port_id'] and 'destination_main_port_id' == group['destination_main_port_id'] and 'container_size' == group['container_size'] and 'container_type' == group['container_type'] and 'commodity' == group['commodity'] and 'shipping_line_id' == group['shipping_line_id']).execute()
    bookings = Shipment.select().where(id == booking_ids)

    if group['importer_exporter_id']:
        bookings = bookings.select().where('importer_exporter_id' == group['importer_exporter_id'])

    bookings_importer_exporters_count = set(bookings.select(bookings.importer_exporter_id).execute()).count()

    containers_from_bookings = ShipmentFclFreightService.select().where('shipment_id' == bookings.select(bookings.id).execute()).sum('containers_count')

    containers_count = [containers_from_spot_searches * POTENTIAL_CONVERSION_RATIO, containers_from_bookings].max()
    importer_exporters_count = [spot_searches_importer_exporters_count * POTENTIAL_CONVERSION_RATIO, bookings_importer_exporters_count].max()

    score = ([containers_count, 1000].min() / 10)

    FclFreightRate.where(group).update('containers_count' == containers_count).execute()
    FclFreightRate.where(group).update('importer_exporters_count' == importer_exporters_count).execute()
    FclFreightRate.where(group).update('priority_score' == int(score)).execute()
    FclFreightRate.where(group).update('priority_score_updated_at' == datetime.now(pytz.utc)).execute()
