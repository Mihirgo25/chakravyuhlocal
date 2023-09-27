from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder
from operator import attrgetter

default_fields = [
    'line_items',
    'is_line_items_error_messages_present',
    'is_line_items_info_messages_present',
    'line_items_error_messages',
    'line_items_info_messages',
    'truck_body_type',
    'transit_time',
    'detention_free_time',
    'validity_start',
    'validity_end',
    'unit',
    'minimum_chargeable_weight'
]

def get_ftl_freight_rate(request):

    if not all_fields_present(request):
        return {}
    ftl_freight_data = find_ftl_freight_rate(request)
    ftl_freight_data = add_possible_charge_codes(ftl_freight_data, request)

    return ftl_freight_data


def all_fields_present(request):
    mandatory_fields = ['origin_location_id','destination_location_id','truck_type','service_provider_id','trip_type','truck_body_type','transit_time','detention_free_time','unit']
    for fields in mandatory_fields:
        if not request.get(fields):
            return False
    return True

def find_ftl_freight_rate(request):
    fields = [getattr(FtlFreightRate, key) for key in default_fields]
    query = FtlFreightRate.select(*fields)

    for key in request:
        if request.get(key) is not None:
            query = query.where(attrgetter(key)(FtlFreightRate) == request[key])
    object = query.first()

    details = {}
    if object:
        details = object.detail()
    return details

def get_ftl_params(request):
    params = {}
    for key in ['origin_location_id','destination_location_id','truck_type','commodity','service_provider_id']:
        params[key] = request.get(key)
    return params

def add_possible_charge_codes(ftl_freight_data, request):
    ftl_params = get_ftl_params(request)
    possible_charge_code = FtlFreightRate(**ftl_params).possible_charge_codes()
    ftl_freight_data =  dict(ftl_freight_data)
    ftl_freight_data['ftl_freight_charge_codes'] = possible_charge_code
    return ftl_freight_data


