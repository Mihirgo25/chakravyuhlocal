import pandas as pd
from database.db_session import db
from joblib import Parallel, delayed
from celery_worker import celery

def haulage_freight_migration():
    from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
    haulage_frieght_rate = HaulageFreightRate.select()
    print("started")
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=rate, is_init_key=True, is_set_location=True, is_audit_data=True) for rate in haulage_frieght_rate.iterator())
    print(len(result))
    return 


def delayed_func(obj, is_init_key=False, is_set_location=False, is_audit_data=False):
    from database.temp_audit_table import TempAudit
    from celery_worker import update_multiple_service_objects
    
    if is_init_key:
        init = ":".join([str(obj.origin_port_id),str(obj.origin_main_port_id or ""), str(obj.destination_port_id), str(obj.destination_main_port_id or ""), str(obj.container_size), str(obj.container_type), str(obj.commodity), str(obj.shipping_line_id), str(obj.service_provider_id), str(obj.importer_exporter_id or ""), str(obj.cogo_entity_id or "")])
        
        obj.init_key = init
        
    if is_set_location:
        set_locations(obj)
    
    if is_audit_data:
        audit_data = list(TempAudit.select(TempAudit.sourced_by_id, TempAudit.procured_by_id).where(TempAudit.object_id == obj.id).dicts())
        print(audit_data)
        if audit_data:
            sorted_data = sorted(audit_data, key = lambda cd: cd["created_at"].date(), reverse=True)[0]
            obj.sourced_by_id = sorted_data["sourced_by_id"]
            obj.procured_by_id = sorted_data["procured_by_id"]
    obj.save()
    update_multiple_service_objects.apply_async(kwargs={"object":obj},queue='low')
    print("Running")
    return True



def set_locations(rate):
    from micro_services.client import maps
    ids = []
    if hasattr(rate, 'origin_port_id') and rate.origin_port_id:
        ids.append(str(rate.origin_port_id))
    if hasattr(rate, 'origin_main_port_id') and rate.origin_main_port_id:
        ids.append(str(rate.origin_main_port_id))
    if hasattr(rate, 'destination_port_id') and rate.destination_port_id:
        ids.append(str(rate.destination_port_id))
    if hasattr(rate, 'destination_main_port_id') and rate.destination_main_port_id:
        ids.append(str(rate.destination_main_port_id))
    if hasattr(rate, 'port_id') and rate.port_id:
        ids.append(str(rate.port_id))    
    if hasattr(rate, 'main_port_id') and rate.main_port_id:
        ids.append(str(rate.main_port_id))
    if hasattr(rate, 'location_id') and rate.location_id:
        ids.append(str(rate.location_id))

    obj = {'filters':{"id": ids, "type":'seaport'}}
    locations_response = maps.list_locations(obj)
    locations = []
    if 'list' in locations_response:
        locations = locations_response["list"]

    for location in locations:
        if hasattr(rate, 'origin_port_id') and str(rate.origin_port_id) == str(location['id']):
            rate.origin_port = get_required_location_data(location)
        if hasattr(rate, 'origin_main_port_id') and str(rate.origin_main_port_id) == str(location['id']):
            rate.origin_main_port = get_required_location_data(location)
        if hasattr(rate, 'destination_port_id') and str(rate.destination_port_id) == str(location['id']):
            rate.destination_port = get_required_location_data(location)
        if hasattr(rate, 'destination_main_port_id') and str(rate.destination_main_port_id) == str(location['id']):
            rate.destination_main_port = get_required_location_data(location)
        if hasattr(rate, 'port_id') and str(rate.port_id) == str(location['id']):
            rate.port = get_required_location_data(location)
        if hasattr(rate, 'main_port_id') and str(rate.main_port_id) == str(location['id']):
            rate.main_port = get_required_location_data(location)
        if hasattr(rate, 'location_id') and str(rate.location_id) == str(location['id']):
            rate.location = get_required_location_data(location)
          


