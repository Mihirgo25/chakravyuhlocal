from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_rate_locals import FclFreightRateLocals
from configs.global_constants import DEFAULT_EXPORT_DESTINATION_DETENTION, DEFAULT_IMPORT_DESTINATION_DETENTION


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        
class FclFreightRate(BaseModel):
    commodity = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField()
    destination_continent_id = UUIDField(index=True, null=True)
    destination_country_id = UUIDField(index=True, null=True)
    destination_demurrage_id = UUIDField(index=True, null=True)
    destination_detention_id = UUIDField(index=True, null=True)
    destination_local = BinaryJSONField(null=True)
    destination_local_id = ForeignKeyField(FclFreightRateLocals, index=True, null=True)
    destination_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_main_port_id = UUIDField(null=True)
    destination_plugin_id = UUIDField(index=True, null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_trade_id = UUIDField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporters_count = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_destination_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_destination_detention_slabs_missing = BooleanField(index=True, null=True)
    is_destination_local_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_destination_local_line_items_info_messages_present = BooleanField(index=True, null=True)
    is_destination_plugin_slabs_missing = BooleanField(index=True, null=True)
    is_origin_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_origin_detention_slabs_missing = BooleanField(index=True, null=True)
    is_origin_local_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_origin_local_line_items_info_messages_present = BooleanField(index=True, null=True)
    is_origin_plugin_slabs_missing = BooleanField(index=True, null=True)
    is_weight_limit_slabs_missing = BooleanField(null=True)
    last_rate_available_date = DateField(null=True)
    omp_dmp_sl_sp = CharField(null=True)
    origin_continent_id = UUIDField(index=True, null=True)
    origin_country_id = UUIDField(index=True, null=True)
    origin_detention_id = UUIDField(index=True, null=True)
    origin_local = BinaryJSONField(null=True)
    origin_local_id = ForeignKeyField(FclFreightRateLocals, index=True, null=True)
    origin_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    origin_main_port_id = UUIDField(null=True)
    origin_plugin_id = UUIDField(index=True, null=True)
    origin_port_id = UUIDField(null=True)
    origin_trade_id = UUIDField(index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    service_provider_id = UUIDField(index=True, null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField()
    validities = BinaryJSONField(null=True)
    weight_limit = BinaryJSONField(null=True)
    weight_limit_id = UUIDField(index=True, null=True)
    port_origin_local = ForeignKeyField(FclFreightRateLocals, backref='fcl_freight_rates', null=True)
    port_destination_local = ForeignKeyField(FclFreightRateLocals, backref='fcl_freight_rates', null=True)

    class Meta:
        table_name = 'fcl_freight_rates'
        indexes = (
            (('container_size', 'container_type', 'commodity'), False),
            (('container_type', 'commodity'), False),
            (('importer_exporter_id', 'service_provider_id'), False),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'importer_exporter_id', 'rate_not_available_entry', 'last_rate_available_date', 'omp_dmp_sl_sp'), False),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('priority_score', 'id', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id', 'importer_exporter_id'), False),
            (('priority_score', 'service_provider_id', 'is_best_price'), False),
            (('priority_score', 'service_provider_id', 'last_rate_available_date'), False),
            (('priority_score', 'service_provider_id', 'rate_not_available_entry'), False),
            (('priority_score', 'service_provider_id', 'shipping_line_id', 'is_best_price'), False),
            (('priority_score', 'service_provider_id', 'shipping_line_id', 'rate_not_available_entry'), False),
            (('service_provider_id', 'id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'commodity'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
        )

# def get_port_origin_local():
#     return None

# def get_port_destination_local():
#     return None

def possible_charge_codes():
    set_origin_port
    set_destination_port
    set_shipping_line

    return None

def set_origin_port(request):
    if request['origin_port']:
        return 
    
    if not request['origin_port_id']:
        return 
    
    # request['origin_port'] = ListLocations.run!(filters: { id: self.origin_port_id }, pagination_data_required: false)[:list].first

def set_destination_port(request):
    if request['origin_port']:
        return 
    
    if not request['origin_port_id']:
        return 

    # request['destination_port'] = ListLocations.run!(filters: { id: self.destination_port_id }, pagination_data_required: false)[:list].first

def set_shipping_line(request):
    if (request['shipping_line']) or (not request['shipping_line_id']):
        return 
    # request['shipping_line'] = ListLocations.run!(filters: { id: self.shipping_line_id }, pagination_data_required: false)[:list].first


def detail(object):
    data = {
        'freight':{
            'id':object['id'],
            'validities':object['validities'],
            'is_best_price':object['is_best_price'],
            'is_rate_expired':object['is_rate_expired'],
            'is_rate_about_to_expire':object['is_rate_about_to_expire'],
            'is_rate_not_available' : object['is_rate_not_available']
        },
        'weight_limit' : object['weight_limit']
    }

#     data = {
#     'freight': object.to_dict(
#         only=['id', 'validities', 'is_best_price'],
#         methods=['is_rate_expired', 'is_rate_about_to_expire', 'is_rate_not_available']
#     ),
#     'weight_limit': object['weight_limit'].to_dict()
# }

    origin_local = {}
    destination_local = {}

    if object['port_origin_local'].get('is_line_items_error_messages_present') == False:
        origin_local['line_items'] = object['port_origin_local'].get('data').get('line_items')
        origin_local['is_line_items_error_messages_present'] = object['port_origin_local']['is_line_items_error_messages_present']
        origin_local['line_items_error_messages'] = object['port_origin_local']['line_items_error_messages']
        origin_local['is_line_items_info_messages_present'] = object['port_origin_local']['is_line_items_info_messages_present']
        origin_local['line_items_info_messages'] = object['port_origin_local']['line_items_info_messages']

    if (not origin_local['line_items']) or (object['is_origin_local_line_items_error_messages_present'] == False):
        origin_local['line_items'] = object['origin_local'].get('line_items')
        origin_local['is_line_items_error_messages_present'] = object['is_origin_local_line_items_error_messages_present']
        origin_local['line_items_error_messages'] = object['origin_local_line_items_error_messages']
        origin_local['is_line_items_info_messages_present'] = object['is_origin_local_line_items_info_messages_present']
        origin_local['line_items_info_messages'] = object['origin_local_line_items_info_messages']

    if object['origin_local'].get('detention').get('free_limit'):
        origin_local['detention'] = object['origin_local']['detention'].update({'is_slabs_missing': object['is_origin_detention_slabs_missing']})
    

    if not origin_local['detention']:
        origin_local['detention'] = object['port_origin_local'].get('data').get('detention').update({'is_slabs_missing': object['port_origin_local'].get('is_detention_slabs_missing')})
    

    if object['origin_local'].get('demurrage').get('free_limit'):
        origin_local['demurrage'] = object['origin_local']['demurrage'].update({'is_slabs_missing': object['is_origin_demurrage_slabs_missing']})

    if (not origin_local['demurrage']):
        origin_local['demurrage'] = object['port_origin_local'].get('data').get('demurrage').update({'is_slabs_missing': object['port_origin_local'].get('is_demurrage_slabs_missing')})

    if object['origin_local'].get('plugin').get('free_limit'):
        origin_local['plugin'] = object['origin_local']['plugin'].update({'is_slabs_missing': object['is_origin_plugin_slabs_missing']})

    if not origin_local['plugin']:
        origin_local['plugin'] = object['port_origin_local'].get('data').get('plugin').update({'is_slabs_missing': object['port_origin_local'].get('is_plugin_slabs_missing')})

    if object['port_destination_local'].get('is_line_items_error_messages_present') == False:
        destination_local['line_items'] = object['port_destination_local'].get('data').get('line_items')
        destination_local['is_line_items_error_messages_present'] = object['port_destination_local']['is_line_items_error_messages_present']
        destination_local['line_items_error_messages'] = object['port_destination_local']['line_items_error_messages']
        destination_local['is_line_items_info_messages_present'] = object['port_destination_local']['is_line_items_info_messages_present']
        destination_local['line_items_info_messages'] = object['port_destination_local']['line_items_info_messages']


    if (not destination_local['line_items']) or object['is_destination_local_line_items_error_messages_present'] == False:
        destination_local['line_items'] = object['destination_local'].get('line_items')
        destination_local['is_line_items_error_messages_present'] = object['is_destination_local_line_items_error_messages_present']
        destination_local['line_items_error_messages'] = object['destination_local_line_items_error_messages']
        destination_local['is_line_items_info_messages_present'] = object['is_destination_local_line_items_info_messages_present']
        destination_local['line_items_info_messages'] = object['destination_local_line_items_info_messages']
    

    if object['destination_local'].get('detention').get('free_limit'):
        destination_local['detention'] = object['destination_local']['detention'].update({'is_slabs_missing': object['is_destination_detention_slabs_missing']})

    if not destination_local['detention']:
        destination_local['detention'] = object['port_destination_local'].get('data').get('detention').update({'is_slabs_missing': object['port_destination_local'].get('is_detention_slabs_missing')})

    if object['destination_local'].get('demurrage').get('free_limit'):
        destination_local['demurrage'] = object['destination_local']['demurrage'].update({'is_slabs_missing': object['is_destination_demurrage_slabs_missing']})
  

    if not destination_local['demurrage']:
        destination_local['demurrage'] = object['port_destination_local'].get('data').get('demurrage').update({'is_slabs_missing': object['port_destination_local'].get('is_demurrage_slabs_missing') })
  

    if object['destination_local'].get('plugin').get('free_limit'):
        destination_local['plugin'] = object['destination_local']['plugin'].update({'is_slabs_missing': object['is_destination_plugin_slabs_missing']})
  

    if not destination_local['plugin']:
        destination_local['plugin'] = object['port_destination_local'].get('data').get('plugin').update({'is_slabs_missing': object['port_destination_local'].get('is_plugin_slabs_missing')})
  

    if not origin_local.get('detention').get('free_limit'):
        origin_local['detention'] = origin_local.get('detention').update({'free_limit': DEFAULT_EXPORT_DESTINATION_DETENTION})
  

    if not destination_local.get('detention').get('free_limit'):
        destination_local['detention'] = destination_local.get('detention').update({'free_limit': DEFAULT_IMPORT_DESTINATION_DETENTION})
  

    return data.update({'origin_local': origin_local, 'destination_local': destination_local })
