from uuid import UUID
from configs.env import *
import json
from micro_services.client import maps
from psycopg2 import sql
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import get_connection
from joblib import delayed, Parallel, cpu_count
import time
import json
import pandas as pd
from configs.definitions import ROOT_DIR

class ParallelJobs:
    def __init__(self):
        self.count_of_cpus = cpu_count()
        self.verbose = 100
    
    def parallel_function(self, parallel_list, columns, procured_sourced_dict, loc_dict, model_name, function_call):
        parallel_pool = Parallel(n_jobs=self.count_of_cpus, prefer="threads", verbose=self.verbose)
        functions = [delayed(function_call)(each, columns, procured_sourced_dict, loc_dict, model_name) for each in parallel_list]
        res = parallel_pool(functions)
        return res

p  = ParallelJobs()

def get_data_in_batches(table_name,parallel = False):

    OFFSET = 0
    limit = 2000

    results = []
    conn = get_connection()

    total_count = 0

    with conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL('select count(id) from {table};').format(table=sql.Identifier(table_name)))
            total_count = cur.fetchall()[0][0]
            cur.close()
    conn.close()

    conn = get_connection()
    columns = None
    with conn:
        with conn.cursor() as cur: 
            while OFFSET <= total_count:
                cur.execute(sql.SQL('SELECT * from {table} order by id desc OFFSET %s LIMIT %s ;').format(table=sql.Identifier(table_name)), [OFFSET, limit])
                result = cur
                if not columns:
                    columns = [col[0] for col in result.description]
                
                if parallel:
                    results = result.fetchall()
                    if table_name == 'air_freight_rate_audits':
                        Parallel(n_jobs=4)(delayed(delay_updation_audits)(row, columns) for row in results)
                    else:
                        Parallel(n_jobs=4)(delayed(delay_freight_rates)(row, columns) for row in results)
                else:
                    results.extend(result.fetchall()) 
                OFFSET = OFFSET + limit
            cur.close()
    conn.close()
    return columns, results

# columns, results = get_data_in_batches('fcl_customs_rates')

def get_audits_in_batches(table_name,object_type):

    OFFSET = 0
    limit = 2000

    results = []
    conn = get_connection()

    total_count = 0

    with conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL('select count(id) from {table} where object_type = %s;').format(table=sql.Identifier(table_name)),[object_type])
            total_count = cur.fetchall()[0][0]
            cur.close()
    conn.close()
    procured_sourced_dict = {}
    conn = get_connection()
    columns = None
    with conn:
        with conn.cursor() as cur: 
            while OFFSET <= total_count:
                cur.execute(sql.SQL('SELECT object_id,sourced_by_id,procured_by_id from {table} where object_type = %s order by created_at desc OFFSET %s LIMIT %s ;').format(table=sql.Identifier(table_name)), [object_type,OFFSET, limit])
                result = cur
                for row in result.fetchall():
                    key = str(row[0])
                    if key not  in procured_sourced_dict.keys():
                        procured_sourced_dict[str(row[0])] = {
                            'procured_by_id':str(row[1]) if row[1] else None,
                            'sourced_by_id':str(row[2]) if row[2] else None
                        }
                OFFSET = OFFSET + limit
            cur.close()
    conn.close()
    return procured_sourced_dict


def get_air_rate_sheets_in_batches():

    OFFSET = 0
    limit = 2000

    results = []
    conn = get_connection()

    total_count = 0

    with conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL('select count(id) from {table} where service_name = %s;').format(table=sql.Identifier('rate_sheets')),['air_freight'])
            total_count = cur.fetchall()[0][0]
            cur.close()
    conn.close()
    procured_sourced_dict = {}
    conn = get_connection()
    columns = None
    with conn:
        with conn.cursor() as cur: 
            while OFFSET <= total_count:
                cur.execute(sql.SQL('SELECT * from {table} where service_name = %s order by created_at desc OFFSET %s LIMIT %s ;').format(table=sql.Identifier('rate_sheets')), ['air_freight',OFFSET, limit])
                result = cur
                if not columns:
                    columns = [col[0] for col in result.description]
                results.extend(result.fetchall()) 
                OFFSET = OFFSET + limit
            cur.close()
    conn.close()
    return columns,results

#################################################     Feedbacks       ##################################################
def air_freight_rate_feedback_migration():
    columns, results = get_data_in_batches('air_freight_rate_feedbacks')
    print(len(results))
    result = Parallel(n_jobs=4)(delayed(delay_updation_feedback)(row, columns) for row in results)
    print("done migrating feedbacks")

    return 
    # except Exception as e:
    #     return all_result

def delay_updation_feedback(row,columns):
    from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
    param = dict(zip(columns, row))
    obj = AirFreightRateFeedback(**param)
    set_locations(obj)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return

#################################################      Requests       ##################################################

def air_freight_rate_requests_migration():
    
    all_result =[]
    columns, results = get_data_in_batches('air_freight_rate_requests')
    result = Parallel(n_jobs=4)(delayed(delay_updation_request)(row, columns) for row in results)
    print("done migrating requests")
    return all_result

def delay_updation_request(row,columns):
    from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
    param = dict(zip(columns, row))
    preferred_airline_ids = param['preferred_airline_ids'] or []
    new_al = []
    for aid in preferred_airline_ids:
        new_al.append(UUID(str(aid)))
    param['preferred_airline_ids'] = new_al
    obj = AirFreightRateRequest(**param)
    # set_locations(obj)
    # get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return

#################################################   Bulk Operation ###########################

def air_freight_rate_bulk_operations_migration():
    columns, results = get_data_in_batches('air_freight_rate_bulk_operations')
    result = Parallel(n_jobs=4)(delayed(delay_updation_bulk_operation)(row, columns) for row in results)
    print('Air Freight Rate Bulk Operations Done')
    return 

def delay_updation_bulk_operation(row,columns):
    from services.air_freight_rate.models.air_freight_rate_bulk_operation import AirFreightRateBulkOperation
    param = dict(zip(columns, row))
    obj = AirFreightRateBulkOperation(**param)
    obj.save(force_insert = True)
    return
    
#################################################   Freight Rates           ###########################


def air_freight_rate_migration():
    columns, results = get_data_in_batches('air_freight_rates',True)
    print('Air Freight Rate Done')
    return 

def delay_freight_rates(row,columns):
    from services.air_freight_rate.models.air_freight_rate import AirFreightRate
    import datetime
    from fastapi.encoders import jsonable_encoder
    param = dict(zip(columns, row))
    param['mode'] = param['source']
    if not param['mode']:
        param['mode'] = 'manual'
    if param['rate_type'] == 'general':
        param['rate_type'] = 'market_place'
    init_key = f'{str(param.get("origin_airport_id"))}:{str(param["destination_airport_id"])}:{str(param["commodity"])}:{str(param["airline_id"])}:{str(param["service_provider_id"])}:{str(param["shipment_type"])}:{str(param["stacking_type"])}:{str(param["cogo_entity_id"] )}:{str(param["commodity_type"])}:{str(param["commodity_sub_type"])}:{str(param["price_type"])}:{str(param["rate_type"])}:{str(param["operation_type"])}:{str(param["mode"])}'
    param['init_key'] = init_key
    obj = AirFreightRate(**param)
    validities = obj.validities
    new_validities = []
    for validity_object in validities:
           if 'status' not in validity_object.keys() or validity_object['status']:
                validity_object['validity_start'] = validity_object['validity_start'].split('T')[0]
                validity_object['validity_end'] = validity_object['validity_end'].split('T')[0]
                new_validities.append(validity_object)

                
    obj.validities = new_validities
    # set_procured_sourced(obj,)
    # set_locations(obj)
    # get_multiple_service_objects(obj)
    try:
        obj.save(force_insert = True)
    except Exception as e:
        print(e)
    return

################################################ Air Freight Rate Locals ########################

def air_freight_rate_locals_migration():
    # procured_sourced_locals_dict = get_audits_in_batches('air_freight_rate_audits','AirFreightRateLocal')
    columns, results = get_data_in_batches('air_freight_rate_locals')
    result = Parallel(n_jobs=4)(delayed(delay_updation_rate_locals)(row, columns) for row in results)
    print('Air Freight Rate Locals Done')
    return 

def delay_updation_rate_locals(row, columns):
    from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
    param = dict(zip(columns, row))
    obj = AirFreightRateLocal(**param)
    param['rate_not_available_entry'] = param['is_active']
    # set_procured_sourced(obj,procured_sourced_dict)
    # set_locations(obj)
    # get_multiple_service_objects(obj)
    
    obj.save(force_insert = True)
    return


################################################ Air Freight Rate Audits ########################

    
def air_freight_rate_audits_migration():
    columns, results = get_data_in_batches('air_freight_rate_audits',True)
    print('Air Freight Rate audits Done')


def delay_updation_audits(row,columns):
    from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
    from services.air_freight_rate.models.air_services_audit import AirServiceAudit
    from database.db_session import db
    param = dict(zip(columns, row))
    object_type = param['object_type']
    if(object_type=='AirFreightRate'):
        obj = AirFreightRateAudit(**param)
        obj.save(force_insert = True)
    else:
        obj = AirServiceAudit(**param)
        print("bedada")
        object_type = obj.object_type
        query="create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(object_type.lower(),object_type.replace("_",""))
        db.execute_sql(query)
        obj.save(force_insert = True)

    return


#########################################################################################
    
def set_locations(rate):
    ids = []
    if hasattr(rate, 'origin_airport_id') and rate.origin_airport_id:
        ids.append(str(rate.origin_airport_id))
    if hasattr(rate, 'destination_airport_id') and rate.destination_airport_id:
        ids.append(str(rate.destination_airport_id))
    
    if hasattr(rate,'airport_id') and rate.airport_id:
        ids.append(str(rate.airport_id))

    obj = {'filters':{"id": ids, "type":'airport'}}
    locations_response = maps.list_locations(obj)
    locations = []
    if 'list' in locations_response:
        locations = locations_response["list"]

    for location in locations:
        if hasattr(rate, 'origin_airport_id') and str(rate.origin_airport_id) == str(location['id']):
            rate.origin_airport = get_required_location_data(location)
        if hasattr(rate, 'destination_airport_id') and str(rate.destination_airport_id) == str(location['id']):
            rate.destination_airport = get_required_location_data(location)
        
        if hasattr(rate,'airport_id') and str(rate.airport_id) == str(location['id']):
            rate.airport = get_required_location_data(location)
          
def get_required_location_data(location):
    loc_data = {
        "id": location["id"],
        "name": location["name"],
        "port_code": location["port_code"],
        "country_id": location["country_id"],
        "continent_id": location["continent_id"],
        "trade_id": location["trade_id"],
        "country_code": location["country_code"]
    }
    return loc_data
          

def spot_search_data(rate):
    from micro_services.client import spot_search
    obj = {'filters':{"id": rate.source_id}}
    spot_search_data = spot_search.list_spot_searches(obj)
    spot_searches = []
    if 'list' in spot_search_data:
        spot_searches = spot_search_data["list"]

    for search in spot_searches:
        if hasattr(rate, 'source_id') and str(rate.source_id) == str(search['id']):
            rate.spot_search = get_required_spot_search_data(search)

def get_required_spot_search_data(search):
    return {
        'id' : search.get('id'), 
        'importer_exporter_id' : search.get('importer_exporter_id'), 
        'importer_exporter' :search.get('importer_exporter'), 
        'service_details' :search.get('service_details')
    }

def set_procured_sourced(obj,procured_sourced_dict):
    obj.procured_by_id = (procured_sourced_dict.get(str(obj.id)) or {}).get('procured_by_id')
    obj.sourced_by_id = (procured_sourced_dict.get(str(obj.id)) or {}).get('sourced_by_id')



def set_location_data(obj,loc_dict):
    obj.location = loc_dict.get(str(obj.location_id))
    

##################################################      TASKS         ######################################

def air_freight_rate_tasks():
    columns, results = get_data_in_batches('air_freight_rate_tasks')
    result = Parallel(n_jobs=4)(delayed(delay_updation_tasks)(row, columns) for row in results)
    print("done migrating tasks")
    return 

def delay_updation_tasks(row,columns):
    from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
    param = dict(zip(columns, row))
    obj = AirFreightRateTasks(**param)
    set_locations(obj)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return

########################################   Surcharges       ######################################
def air_freight_rate_surcharge_migration():
    all_result=[]
    # procured_sourced_locals_dict = get_audits_in_batches('air_freight_rate_audits','AirFreightRateSurcharge')
    columns, results = get_data_in_batches('air_freight_rate_surcharges')
    print("Fetching Data Completed")
    result = Parallel(n_jobs=4)(delayed(delay_updation_rate_surcharges)(row, columns) for row in results)
    print('Air Freight Rate Locals Done')
    return all_result

def delay_updation_rate_surcharges(row, columns):
    from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
    param = dict(zip(columns, row))
    param['rate_not_available_entry'] = param['is_active']
    obj = AirFreightRateSurcharge(**param)
    # set_procured_sourced(obj,procured_sourced_dict)
    # set_locations(obj)
    # get_multiple_service_objects(obj)
    
    obj.save(force_insert = True)
    return

#######################################      Rate Sheets ####################

def rate_sheets():
    columns, results = get_air_rate_sheets_in_batches()
    result = Parallel(n_jobs=4)(delayed(delay_rate_sheets)(row, columns) for row in results)

def delay_rate_sheets(row,columns):
    from services.rate_sheet.models.rate_sheet import RateSheet
    param = dict(zip(columns, row))
    obj = RateSheet(**param)
    obj.save(force_insert = True)
    return




##################################################################


def run_migration():
    # procured_by_sourced_by('air_freight_rate_local')
    # all_locations_data()
    # air_freight_rate_feedback_migration()
    air_freight_rate_audits_migration()
    # air_freight_rate_bulk_operations_migration()
    # air_freight_rate_requests_migration()
    # air_freight_storage_rates_migration()
    # air_freight_warehouse_rates_migration()
    # air_freight_rate_locals_migration()
    # air_freight_rate_surcharge_migration()
    # air_freight_rate_tasks()
    air_freight_rate_migration()
    # rate_sheets()
    # update_locations_for_air_freight()
    # set_all_airlines()
    # set_all_sps()
    update_locations_for_air_freight_surcharge()




# ###############################################################################################

def update_locations_for_air_freight():
    from services.air_freight_rate.models.air_freight_rate import AirFreightRate
    from fastapi.encoders import jsonable_encoder
    origin_airport_ids = AirFreightRate.select(AirFreightRate.origin_airport_id.distinct())
    destination_airport_ids = AirFreightRate.select(AirFreightRate.destination_airport_id.distinct())
    origin_airport_ids = jsonable_encoder(list(origin_airport_ids.dicts()))
    destination_airport_ids = jsonable_encoder(list(destination_airport_ids.dicts()))
    set_locations(location_ids = origin_airport_ids,service = 'AirFreightRate',origin=True)
    set_locations(location_ids = destination_airport_ids,service='AirFreightRate',destination=True)

    airlines = AirFreightRate.select(AirFreightRate.airline_id.distinct())
    airline_ids = jsonable_encoder(list(airlines.dicts()))

def update_locations_for_air_freight_local():
    from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
    from fastapi.encoders import jsonable_encoder
    airport_ids = AirFreightRateLocal.select(AirFreightRateLocal.airport_id.distinct())
    airport_ids = jsonable_encoder(list(airport_ids.dicts()))
    set_locations(location_ids = airport_ids,service = 'AirFreightRateLocal')

def update_locations_for_air_freight_request():
    from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
    from fastapi.encoders import jsonable_encoder
    origin_airport_ids = AirFreightRateRequest.select(AirFreightRateRequest.origin_airport_id.distinct())
    destination_airport_ids = AirFreightRateRequest.select(AirFreightRateRequest.destination_airport_id.distinct())
    origin_airport_ids = jsonable_encoder(list(origin_airport_ids.dicts()))
    destination_airport_ids = jsonable_encoder(list(destination_airport_ids.dicts()))
    set_locations(location_ids = origin_airport_ids,service = 'AirFreightRateRequest',origin=True)
    set_locations(location_ids = destination_airport_ids,service='AirFreightRateRequest',destination=True)

def update_locations_for_air_freight_surcharge():
    from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
    from fastapi.encoders import jsonable_encoder
    origin_airport_ids = AirFreightRateSurcharge.select(AirFreightRateSurcharge.origin_airport_id.distinct())
    destination_airport_ids = AirFreightRateSurcharge.select(AirFreightRateSurcharge.destination_airport_id.distinct())
    origin_airport_ids = jsonable_encoder(list(origin_airport_ids.dicts()))
    destination_airport_ids = jsonable_encoder(list(destination_airport_ids.dicts()))
    set_locations(location_ids = origin_airport_ids,service = 'AirFreightRateSurcharge',origin=True)
    set_locations(location_ids = destination_airport_ids,service='AirFreightRateSurcharge',destination=True)



def set_locations(location_ids,service,origin=False,destination=False,airport=False):
    from micro_services.client import maps
    from services.air_freight_rate.models.air_freight_rate import AirFreightRate
    from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
    from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
    from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
    locations = []
    if origin:
        key = 'origin_airport_id'
    else:
        key = 'destination_airport_id'
    for location_id in location_ids:
        locations.append(location_id[key])
    
    total_count = len(locations)
    offset = 0
    limit = 200
    loops = int(total_count/limit)
    rem = total_count%limit
    if rem:
        loops = loops+1

    for index in range(0,loops):
        locations_temp = locations[offset:offset+limit]
        obj = {'filters':{"id": locations_temp, "type":'airport'},'page_limit':limit}
        locations_list = maps.list_locations(obj)
        offset = limit+offset
        if 'list' in locations_list:
            locations = locations_list['list']
            for location in locations:
                location = get_required_location_data(location)
                if service == 'AirFreightRate':
                    if origin:
                        AirFreightRate.update(origin_airport=location).where(
                            AirFreightRate.origin_airport_id == location['id']
                        ).execute()
                    else:
                        AirFreightRate.update(destination_airport=location).where(
                            AirFreightRate.destination_airport_id == location['id']
                            ).execute()
                
                if service == 'AirFreightRateRequest':
                    if origin:
                        AirFreightRateRequest.update(origin_airport=location).where(
                            AirFreightRateRequest.origin_airport_id == location['id']
                        ).execute()
                    else:
                        AirFreightRateRequest.update(destination_airport=location).where(
                            AirFreightRateRequest.destination_airport_id == location['id']
                            ).execute()

                if service == 'AirFreightRateSurcharge':
                    if origin:
                        AirFreightRateSurcharge.update(origin_airport=location).where(
                            AirFreightRateSurcharge.origin_airport_id == location['id']
                        ).execute()
                    else:
                        AirFreightRateSurcharge.update(destination_airport=location).where(
                            AirFreightRateSurcharge.destination_airport_id == location['id']
                            ).execute()                            

                if service == 'AirFreightRateLocal':
                    AirFreightRateLocal.update(airport = location).where(
                        AirFreightRateLocal.airport_id == location['id']
                    )
        if rem and index==loops-1:
            limit = rem

######################################################################################################
def set_all_airlines():
    from services.air_freight_rate.models.air_freight_rate import AirFreightRate
    from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
    from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal 
    from fastapi.encoders import jsonable_encoder
    freight_rate_airline_ids = AirFreightRate.select(AirFreightRate.airline_id.distinct())
    freight_rate_airline_ids = jsonable_encoder(list(freight_rate_airline_ids.dicts()))
    set_airlines(airlines = freight_rate_airline_ids,service = 'AirFreightRate')

    local_rate_ariline_ids = AirFreightRateLocal.select(AirFreightRateLocal.airline_id.distinct())
    local_rate_ariline_ids = jsonable_encoder(list(local_rate_ariline_ids.dicts()))
    set_airlines(airlines = local_rate_ariline_ids,service='AirFreightRateLocal')

    surcharge_rate_airline_ids = AirFreightRateSurcharge.select(AirFreightRateSurcharge.airline_id.distinct())
    surcharge_rate_airline_ids = jsonable_encoder(list(surcharge_rate_airline_ids.dicts()))
    set_airlines(airlines = surcharge_rate_airline_ids,service='AirFreightRateSurcharge')



def set_airlines(airlines,service):
    from services.air_freight_rate.models.air_freight_rate import AirFreightRate
    from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
    from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
    from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
    from database.rails_db import get_operators

    airlines_ids = []
    for airline in airlines:
        airlines_ids.append(airline['airline_id'])
    
    total_count = len(airlines_ids)
    offset = 0
    limit = 200
    loops = int(total_count/limit)
    rem = total_count%limit
    if rem:
        loops = loops+1
    
    for index in range(0,loops):
        if rem and index==loops-1:
            limit = rem
        airline_temp = airlines_ids[offset:offset+limit]
        airlines = get_operators(id=airline_temp,operator_type= 'airline')
        offset = limit+offset
        if airlines:
            for airline in airlines:
                if service == 'AirFreightRate':
                    t = AirFreightRate.update(airline=airline).where(
                        AirFreightRate.airline_id == airline['id']
                        ).execute()
                
                if service == 'AirFreightRateSurcharge':
                    AirFreightRateSurcharge.update(airline=airline).where(
                        AirFreightRateSurcharge.airline_id == airline['id']
                        ).execute()                            

                if service == 'AirFreightRateLocal':
                    AirFreightRateLocal.update(airline=airline).where(
                        AirFreightRateLocal.airline_id == airline['id']
                    )


#####################################################################################################

def set_all_sps():
    from services.air_freight_rate.models.air_freight_rate import AirFreightRate
    from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
    from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal 
    from fastapi.encoders import jsonable_encoder
    freight_rate_service_provider_ids = AirFreightRate.select(AirFreightRate.service_provider_id.distinct())
    freight_rate_service_provider_ids = jsonable_encoder(list(freight_rate_service_provider_ids.dicts()))
    set_service_provider(service_providers = freight_rate_service_provider_ids,service = 'AirFreightRate')

    local_rate_service_provider_ids = AirFreightRateLocal.select(AirFreightRateLocal.service_provider_id.distinct())
    local_rate_service_provider_ids = jsonable_encoder(list(local_rate_service_provider_ids.dicts()))
    set_service_provider(service_providers = local_rate_service_provider_ids,service='AirFreightRateLocal')

    surcharge_rate_service_provider_ids = AirFreightRateSurcharge.select(AirFreightRateSurcharge.service_provider_id.distinct())
    surcharge_rate_service_provider_ids = jsonable_encoder(list(surcharge_rate_service_provider_ids.dicts()))
    set_service_provider(service_providers = surcharge_rate_service_provider_ids,service='AirFreightRateSurcharge')


def set_service_provider(service_providers,service):
    from services.air_freight_rate.models.air_freight_rate import AirFreightRate
    from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
    from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
    from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
    from database.rails_db import get_organization
    service_provider_ids = []
    for service_provider in service_providers:
        service_provider_ids.append(service_provider['service_provider_id'])
    
    total_count = len(service_provider_ids)
    offset = 0
    limit = 200
    loops = int(total_count/limit)
    rem = total_count%limit
    if rem:
        loops = loops+1
    
    for index in range(0,loops):
        if rem and index==loops-1:
            limit = rem
        service_provider_temp = service_provider_ids[offset:offset+limit]
        service_providers = get_organization(id=service_provider_temp)
        offset = limit+offset
        if service_providers:
            for sp in service_providers:
                if service == 'AirFreightRate':
                    t = AirFreightRate.update(service_provider=sp).where(
                        AirFreightRate.service_provider_id == sp['id']
                        ).execute()
                
                if service == 'AirFreightRateSurcharge':
                    AirFreightRateSurcharge.update(service_provider=sp).where(
                        AirFreightRateSurcharge.service_provider_id == sp['id']
                        ).execute()                            

                if service == 'AirFreightRateLocal':
                    AirFreightRateLocal.update(service_provider=sp).where(
                        AirFreightRateLocal.service_provider_id == sp['id']
                    )


####################################################################

def migrate_request_audits(audit):
    conn = get_connection()
    columns = None
    results = []
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL('select * from {table} where object_type = %s;').format(table=sql.Identifier('air_freight_rate_audits')),[audit])
            results = cur
            if not columns:
                columns = [col[0] for col in results.description]
            Parallel(n_jobs=4)(delayed(delay_request_feebacks_audits)(row, columns) for row in results.fetchall())
            cur.close()
    conn.close()

def delay_request_feebacks_audits(row,columns):
    from services.air_freight_rate.models.air_services_audit import AirServiceAudit
    from database.db_session import db
    param = dict(zip(columns, row))
    obj = AirServiceAudit(**param)
    obj.save(force_insert = True)
    return

def request_and_feedback():
    migrate_request_audits('AirFreightRateFeedback')
    migrate_request_audits('AirFreightRateRequest')




    





