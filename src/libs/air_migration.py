from configs.env import *
import json
from micro_services.client import maps
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import get_connection
from joblib import delayed, Parallel, cpu_count
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_bulk_operation import AirFreightRateBulkOperation
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

######################### FCL Customs Migration ##################################################

# def fcl_customs_rates_migration():
#     file_path = "zone_data.json"
#     with open(file_path, 'r') as file:
#         zone_data = json.load(file)

#     procured_ids_path = "procured_by_sourced_by_customs.json"
#     with open(procured_ids_path, 'r') as file:
#         procured_sourced_customs_dict = json.load(file)
    
#     location_data_path = 'location_data_customs.json'
#     with open(location_data_path, 'r') as file:
#         loc_dict = json.load(file)

#     all_result =[]
#     try:
#         conn = get_connection()
#         with conn:
#             with conn.cursor() as cur:
#                 sql_query = """
#                 SELECT * from fcl_customs_rates
#                 """   
#                 cur.execute(sql_query,)
#                 result = cur

#                 columns = [col[0] for col in result.description]
#                 p.parallel_function(result.fetchall(), columns, zone_data, procured_sourced_customs_dict, loc_dict, func_in_parallel)  
#                 cur.close()
#         conn.close()
#         print('FCL Customs Done')
#         return all_result
#     except Exception as e:
#         return all_result

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
    from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
    all_result =[]
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql_query = "SELECT * FROM air_freight_rate_requests limit 1000"
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]    
            result = Parallel(n_jobs=4)(delayed(delay_updation_request)(row, columns) for row in result.fetchall())
            cur.close()
            cur.close()
    conn.close()
    print("done migrating requests")
    return all_result

def delay_updation_request(row,columns):
    param = dict(zip(columns, row))
    obj = AirFreightRateRequest(**param)
    set_locations(obj)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return


# def fcl_customs_rate_bulk_operation_migration():
#     from services.fcl_customs_rate.models.fcl_customs_rate_bulk_operation import FclCustomsRateBulkOperation
#     all_result =[]
#     try:
#         conn = get_connection()
#         with conn:
#             with conn.cursor() as cur:
                    
#                 sql_query = "SELECT * FROM fcl_customs_rate_bulk_operations"
#                 cur.execute(sql_query,)
#                 result = cur.fetchall()
 
#             for res in result:
#                 new_obj = {
#                     "id": str(res[0]),   
#                     "progress": res[1],   
#                     "action_name": res[2],   
#                     "performed_by_id": str(res[3]),   
#                     "data": res[4],
#                     "created_at": res[5],
#                     "updated_at": res[6],
#                     "service_provider_id":str(res[7])
#                 }
#                 all_result.append(new_obj)
#             cur.close()
#         FclCustomsRateBulkOperation.insert_many(all_result).execute()
#         conn.close()
#         print('FCL Customs Bulk Operation Done')
#         return all_result
#     except Exception as e:
#         return all_result

def air_freight_rate_migration():
    all_result=[]
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql_query = """
            SELECT * FROM air_freight_rates limit 100
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]
            result = Parallel(n_jobs=4)(delayed(delay_updation_rate)(row, columns) for row in result.fetchall())  
            cur.close()
    conn.close()
    print('Air Freight Rate Done')
    return all_result

def delay_updation_rate(row,columns):
    param = dict(zip(columns, row))
    obj = AirFreightRate(**param)
    set_locations(obj)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return

def air_freight_rate_locals_migration():
    all_result=[]
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql_query = """
            SELECT * FROM air_freight_rate_locals limit 500
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]
            result = Parallel(n_jobs=4)(delayed(delay_updation_rate_locals)(row, columns) for row in result.fetchall())  

            cur.close()
    conn.close()
    print('Air Freight Rate Locals Done')
    return all_result

def delay_updation_rate_locals(row, columns):
    param = dict(zip(columns, row))
    obj = AirFreightRateLocal(**param)
    
    set_locations(obj)
    get_multiple_service_objects(obj)
    set_procured_sourced(obj,procured_sourced_dict)
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
            FROM air_freight_rate_audits limit 1000
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]    
            result = Parallel(n_jobs=4)(delayed(delay_updation_audits)(row, columns) for row in result.fetchall())
            cur.close()
    conn.close()
    print('Air Freight Rate audits Done')
    return all_result


def delay_updation_audits(row,columns):
    param = dict(zip(columns, row))
    obj = AirFreightRateAudit(**param)
    obj.save(force_insert = True)
    return

# def air_freight_storage_rates_migration():
#     from services.air_freight_rate.models.air_freight_storage_rate import AirFreightStorageRates
#     procured_ids_path = "procured_by_sourced_by_storage.json"
#     with open(procured_ids_path, 'r') as file:
#         procured_sourced_cfs_dict = json.load(file)
    
#     location_data_path = 'location_data_cfs.json'
#     with open(location_data_path, 'r') as file:
#         loc_dict = json.load(file)

#     all_result =[]
#     conn = get_connection()
#     with conn:
#         with conn.cursor() as cur:
#             sql_query = """
#             SELECT * from air_freight_storage_rates
#             """   
#             cur.execute(sql_query,)
#             result = cur
                            
#             columns = [col[0] for col in result.description]    
#             for row in result.fetchall():
#                 param = dict(zip(columns, row))
#                 obj = AirFreightStorageRate(**param)
#                 obj.save(force_insert = True)
#             cur.close()
#     conn.close()
#     print('Air Freight Storage Rates migration Done')
#     return all_result


################################## FCL CFS Migration ############################################

# def fcl_cfs_rate_requests_migration():
#     from services.fcl_cfs_rate.models.fcl_cfs_rate_request import FclCfsRateRequest
#     all_result =[]
#     try:
#         conn = get_connection()
#         with conn:
#             with conn.cursor() as cur:
#                 sql_query = "SELECT * FROM fcl_cfs_rate_requests"
#                 cur.execute(sql_query,)
#                 result = cur

#                 columns = [col[0] for col in result.description]
#                 for row in result.fetchall():
#                     param = dict(zip(columns, row))
#                     param['commodity'] = param['commodity'] if param['commodity'] else None
#                     obj = FclCfsRateRequest(**param)
#                     set_locations(obj)
#                     spot_search_data(obj)
#                     get_multiple_service_objects(obj)
#                     obj.save(force_insert = True)
#                 cur.close()
#             conn.close()
#         print('CFS requests done')
#         return all_result
#     except Exception as e:
#         return all_result

# def fcl_cfs_rate_bulk_operation_migration():
#     from services.fcl_cfs_rate.models.fcl_cfs_rate_bulk_operation import FclCfsRateBulkOperation
#     all_result =[]
#     try:
#         conn = get_connection()
#         with conn:
#             with conn.cursor() as cur:
#                 sql_query = "SELECT * FROM fcl_cfs_rate_bulk_operations"
#                 cur.execute(sql_query,)
#                 result = cur.fetchall()
 
#             for res in result:
#                 new_obj = {
#                     "id": str(res[0]),   
#                     "progress": res[1],   
#                     "action_name": res[2],   
#                     "performed_by_id": str(res[3]),   
#                     "data": res[4],
#                     "created_at": res[5],
#                     "updated_at": res[6],
#                     "service_provider_id":str(res[7])
#                 }
                
#                 all_result.append(new_obj)
#                 cur.close()
#         FclCfsRateBulkOperation.insert_many(all_result).execute()
#         conn.close()
#         return all_result
#     except Exception as e:
#         return all_result
    
# def fcl_cfs_rate_audits_migration():
#     from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
#     all_result = []
#     try:
#         conn = get_connection()
#         with conn:
#             with conn.cursor() as cur:
#                 sql_query = "SELECT * FROM fcl_cfs_rate_audits"
#                 cur.execute(sql_query,)
#                 result = cur.fetchall()
#              
#                 cur.close()
#         conn.close()
#         print('CFS audits done')
#         return all_result
#     except Exception as e:
#         return all_result
    
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
          
# def get_required_location_data(location):
#     loc_data = {
#         "id": location["id"],
#         "name": location["name"],
#         "is_icd": location["is_icd"],
#         "port_code": location["port_code"],
#         "country_id": location["country_id"],
#         "continent_id": location["continent_id"],
#         "trade_id": location["trade_id"],
#         "country_code": location["country_code"]
#     }
#     return loc_data

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


def set_procured_sourced(obj):
    obj.procured_by_id = (procured_sourced_dict.get(str(obj.id)) or {}).get('procured_by_id')
    obj.sourced_by_id = (procured_sourced_dict.get(str(obj.id)) or {}).get('sourced_by_id')

def procured_by_sourced_by(model):
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                if model == 'air_freight_rate_locals':
                    sql_query = "select object_id, procured_by_id, sourced_by_id from air_freight_rate_audits where object_type = 'AirFreightRate'"
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
        if model == 'air_freight_storage_rate':
            file_path = "procured_by_sourced_by_storage.json"
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

def all_locations_data():
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                                
                sql_query = """select id, name, port_code, country_id,country_code, continent_id,trade_id from locations"""
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
        if model == 'air_freight_storage_rate':
            file_path = "procured_by_sourced_by_storage.json"
        else:
            file_path = "procured_by_sourced_by_cfs.json"
        with open(file_path, 'w') as file:
            json.dump(procured_sourced_dict, file)
    except Exception as e:
        return None
    
    
def run_migration():
    procured_by_sourced_by('air_freight_rate_locals')
    # all_locations_data()
    print('Procured by Sourced by Data done')
    # air_freight_rate_migration()
    # air_freight_rate_locals_migration()
    # air_freight_rate_feedback_migration()
    # air_freight_rate_audits_migration()
    # air_freight_rate_requests_migration()
    # air_freight_storage_rates_migration()
    # air_freight_warehouse_rates_migration()