import pandas as pd
from database.db_session import db
from joblib import Parallel, delayed
from celery_worker import celery

def fcl_freight_migration():
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
    fcl_freight_rates = FclFreightRate.select()
    print("started")
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=rate, is_init_key=True, is_set_location=True, is_audit_data=True) for rate in fcl_freight_rates.iterator())
    print(len(result))
    
def fcl_local_migration():
    from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
    fcl_locals = FclFreightRateLocal.select()
    print("started")
    result = Parallel(n_jobs=4)(delayed(delayed_func)(opj=rate, is_set_location=True, is_audit_data=True) for rate in fcl_locals.iterator())
    print(len(result))
    
def fcl_freight_bulk_operation():
    from services.fcl_freight_rate.models.fcl_freight_rate_bulk_operation import FclFreightRateBulkOperation
    bulks = FclFreightRateBulkOperation.select()
    print("started")
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=bulk, is_audit_data=True) for bulk in bulks.iterator())
    
def commodity_surchaurge():
    from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
    objects = FclFreightRateCommoditySurcharge.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj) for obj in objects.iterator())
    
def extension_rule_set():
    from services.fcl_freight_rate.models.fcl_freight_rate_extension_rule_set import FclFreightRateExtensionRuleSet
    objects = FclFreightRateExtensionRuleSet.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj) for obj in objects.iterator())
    
def rate_feedback():
    from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
    objects = FclFreightRateFeedback.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj) for obj in objects.iterator())
    
def free_day_request():
    from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
    objects = FclFreightRateFreeDayRequest.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj, is_set_location=True) for obj in objects.iterator())
    
def free_day():
    from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
    objects = FclFreightRateFreeDay.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj, is_set_location=True, is_audit_data=True) for obj in objects.iterator())

def local_agent():
    from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
    objects = FclFreightRateLocalAgent.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj, is_set_location=True) for obj in objects.iterator())
    
def local_request():
    from services.fcl_freight_rate.models.fcl_freight_rate_local_request import FclFreightRateLocalRequest
    objects = FclFreightRateLocalRequest.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj, is_set_location=True) for obj in objects.iterator())
    
def rate_request():
    from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
    objects = FclFreightRateRequest.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj, is_set_location=True) for obj in objects.iterator())
    
def seasonal_surcharge():
    from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
    objects = FclFreightRateSeasonalSurcharge.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj, is_set_location=True, is_audit_data=True) for obj in objects.iterator())
    
def rate_task():
    from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
    objects = FclFreightRateTask.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj, is_set_location=True) for obj in objects.iterator())
    
def weight_limit():
    from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
    objects = FclFreightRateWeightLimit.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj, is_set_location=True) for obj in objects.iterator())
    
def weight_configuration():
    from services.fcl_freight_rate.models.fcl_weight_slabs_configuration import FclWeightSlabsConfiguration
    objects = FclWeightSlabsConfiguration.select()
    result = Parallel(n_jobs=4)(delayed(delayed_func)(obj=obj) for obj in objects.iterator())
         
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
          
def get_required_location_data(location):
    loc_data = {
        "id": location["id"],
        "name": location["name"],
        "is_icd": location["is_icd"],
        "port_code": location["port_code"],
        "country_id": location["country_id"],
        "continent_id": location["continent_id"],
        "trade_id": location["trade_id"],
        "country_code": location["country_code"]
    }
    return loc_data

def create_partition_table():
    df = pd.read_csv("/Users/abhishek/ocean-rms/origin_port_id29.csv")
    for idx, row in df.iterrows():
        origin_port_id = str(row["origin_port_id"])
        query = "create table if not exists fcl_freight_rates_{} partition of fcl_freight_rates for values in ('{}')".format(origin_port_id.replace("-", "_"), origin_port_id)
        db.execute_sql(query)
        print(idx)