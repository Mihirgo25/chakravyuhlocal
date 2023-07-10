from uuid import UUID
from configs.env import *
import json
from micro_services.client import maps
from psycopg2 import sql
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import get_connection
from joblib import delayed, Parallel, cpu_count
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_bulk_operation import AirFreightRateBulkOperation
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from libs.migration import delayed_func

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

def get_data_in_batches(table_name):

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
                results.extend(result.fetchall()) 
                OFFSET = OFFSET + limit
            cur.close()
    conn.close()
    return columns, results

# columns, results = get_data_in_batches('fcl_customs_rates')


def air_freight_rate_feedback_migration():
    from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
    all_result = []
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
                
            sql_query = """
            SELECT feedback.*,
                rate.origin_airport_id,
                rate.origin_country_id,
                rate.origin_continent_id,
                rate.origin_trade_id,
                rate.destination_airport_id,
                rate.destination_continent_id,
                rate.destination_trade_id,
                rate.cogo_entity_id,
                rate.service_provider_id,
                rate.destination_country_id,
                rate.commodity,
                rate.airline_id,
                rate.operation_type
            FROM air_freight_rate_feedbacks feedback
            INNER JOIN air_freight_rates rate
            ON rate.id = feedback.air_freight_rate_id limit 1000
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]    
            result = Parallel(n_jobs=4)(delayed(delay_updation_feedback)(row, columns) for row in result.fetchall())
            cur.close()
    conn.close()
    print('Air Freight Rate Feedbacks Done')
    return all_result
    # except Exception as e:
    #     return all_result

def delay_updation_feedback(row,columns):
    param = dict(zip(columns, row))
    obj = AirFreightRateFeedback(**param)
    set_locations(obj)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return

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
        new_al.append(UUID(aid))
    param['preferred_airline_ids'] = new_al
    obj = AirFreightRateRequest(**param)
    set_locations(obj)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return



def air_freight_rate_bulk_operations_migration():
    from services.air_freight_rate.models.air_freight_rate_bulk_operation import AirFreightRateBulkOperation
    all_result = []
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
                
            sql_query = """
            SELECT * FROM air_freight_rate_bulk_operations
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]    
            result = Parallel(n_jobs=4)(delayed(delay_updation_bulk_operation)(row, columns) for row in result.fetchall())
            cur.close()
    conn.close()
    print('Air Freight Rate Bulk Operations Done')
    return all_result

def delay_updation_bulk_operation(row,columns):
    param = dict(zip(columns, row))
    obj = AirFreightRateBulkOperation(**param)
    obj.save(force_insert = True)
    return
    

def air_freight_rate_migration():
    all_result=[]
    procured_ids_path = "procured_by_sourced_by_rates.json"
    with open(procured_ids_path, 'r') as file:
        procured_sourced_rates_dict = json.load(file)
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql_query = """
            SELECT * FROM air_freight_rates limit 100
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]
            result = Parallel(n_jobs=4)(delayed(delay_updation_rate)(row, columns,procured_sourced_rates_dict) for row in result.fetchall())  
            cur.close()
    conn.close()
    print('Air Freight Rate Done')
    return all_result

def delay_updation_rate(row,columns,procured_sourced_dict):
    param = dict(zip(columns, row))
    obj = AirFreightRate(**param)
    set_procured_sourced(obj,procured_sourced_dict)
    set_locations(obj)
    get_multiple_service_objects(obj)
    
    obj.save(force_insert = True)
    return

def air_freight_rate_locals_migration():
    all_result=[]
    procured_ids_path = "procured_by_sourced_by_locals.json"
    with open(procured_ids_path, 'r') as file:
        procured_sourced_locals_dict = json.load(file)
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql_query = """
            SELECT * FROM air_freight_rate_locals limit 500
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]
            result = Parallel(n_jobs=4)(delayed(delay_updation_rate_locals)(row, columns,procured_sourced_locals_dict) for row in result.fetchall())  

            cur.close()
    conn.close()
    print('Air Freight Rate Locals Done')
    return all_result

def delay_updation_rate_locals(row, columns,procured_sourced_dict):
    param = dict(zip(columns, row))
    obj = AirFreightRateLocal(**param)
    set_procured_sourced(obj,procured_sourced_dict)
    set_locations(obj)
    get_multiple_service_objects(obj)
    
    obj.save(force_insert = True)
    return



    
def air_freight_rate_audits_migration():
    from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
    all_result = []
    # try:
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql_query = """
            SELECT * 
            FROM air_freight_rate_audits limit 100000
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]   
            result = Parallel(n_jobs=4)(delayed(delay_updation_audits)(row, columns,row[3]) for row in result.fetchall())
            cur.close()
    conn.close()
    print('Air Freight Rate audits Done')
    return all_result


def delay_updation_audits(row,columns,object_type):
    param = dict(zip(columns, row))
    if(object_type=='AirFreightRate'):
        obj = AirFreightRateAudit(**param)
        obj.save(force_insert = True)
    else:
        obj = AirServiceAudit(**param)
        obj.save(force_insert = True)

    return
    
def set_locations(rate):
    ids = []
    if hasattr(rate, 'origin_airport_id') and rate.origin_airport_id:
        ids.append(str(rate.origin_airport_id))
    if hasattr(rate, 'destination_airport_id') and rate.destination_airport_id:
        ids.append(str(rate.destination_airport_id))

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

def func_in_parallel(row, columns, procured_sourced_dict, model_name):
    param = dict(zip(columns, row))
    
    obj = AirFreightRate(**final_params)
    set_procured_sourced(obj,procured_sourced_dict)
    set_location_data(obj,loc_dict)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)


def set_procured_sourced(obj,procured_sourced_dict):
    obj.procured_by_id = (procured_sourced_dict.get(str(obj.id)) or {}).get('procured_by_id')
    obj.sourced_by_id = (procured_sourced_dict.get(str(obj.id)) or {}).get('sourced_by_id')

def procured_by_sourced_by(model):
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                if model == 'air_freight_rate_local':
                    sql_query = "select object_id, procured_by_id, sourced_by_id from air_freight_rate_audits where object_type = 'AirFreightRateLocal'"
                else:
                    sql_query = "select object_id, procured_by_id, sourced_by_id from fcl_cfs_rate_audits where object_type = 'FclCfsRate'"
                cur.execute(sql_query,)
                result = cur
                procured_sourced_dict = {}
                for row in result.fetchall():
                    procured_sourced_dict[str(row[0])] = {
                        'procured_by_id':str(row[1]) if row[1] else None,
                        'sourced_by_id':str(row[2]) if row[2] else None
                    }
                cur.close()
        conn.close()
        if model == 'air_freight_rate_local':
            file_path = "procured_by_sourced_by_locals.json"
        else:
            file_path = "procured_by_sourced_by_cfs.json"
        with open(file_path, 'w') as file:
            json.dump(procured_sourced_dict, file)
    except Exception as e:
        return None

def get_locations():
    FILE_PATH = os.path.join(ROOT_DIR, "loc_for_cfs.csv")
    loc_data = pd.read_csv(FILE_PATH)
    loc_dict = {}
    for index, row in loc_data.iterrows():
        loc_dict[row['id']] = {
            'id':row['id'],
            'name':row['name'],
            'is_icd':row['is_icd'],
            'port_code':row['port_code'],
            'country_id':row['country_id'],
            'continent_id':row['continent_id'],
            'trade_id':row['trade_id'],
            'country_code':row['country_code']
        }

    file_path = "location_data_cfs.json"

    with open(file_path, 'w') as file:
        json.dump(loc_dict, file)

def set_location_data(obj,loc_dict):
    obj.location = loc_dict.get(str(obj.location_id))
    
    
def run_migration():
    procured_by_sourced_by('air_freight_rate_local')
    # all_locations_data()
    print('Procured by Sourced by Data done')
    # air_freight_rate_feedback_migration()
    air_freight_rate_audits_migration()
    # air_freight_rate_bulk_operations_migration()
    # air_freight_rate_requests_migration()
    # air_freight_storage_rates_migration()
    # air_freight_warehouse_rates_migration()
    # air_freight_rate_locals_migration()