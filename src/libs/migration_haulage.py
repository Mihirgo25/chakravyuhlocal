from configs.env import *
import json
from micro_services.client import maps
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import get_connection
from joblib import delayed, Parallel, cpu_count
from services.haulage_freight_rate.models.haulage_freight_rate_feedback import HaulageFreightRateFeedback
from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_bulk_operation import HaulageFreightRateBulkOperation
from libs.migration import delayed_func
import json
import pandas as pd
from configs.definitions import ROOT_DIR

######################### Haulage freight rate feedback Migration ##################################################


def haulage_freight_rate_feedback_migration():
    from services.haulage_freight_rate.models.haulage_freight_rate_feedback import HaulageFreightRateFeedback
    all_result = []
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
                
            sql_query = """
            SELECT feedback.*,
                rate.origin_location_id,
                rate.origin_country_id,
                rate.origin_city_id,
                rate.destination_location_id,
                rate.service_provider_id,
                rate.destination_country_id,
                rate.destination_city_id,
                rate.commodity,
                rate.container_size,
                rate.container_type,
                rate.trailer_type,
                rate.haulage_type,
                rate.trip_type
            FROM haulage_freight_rate_feedbacks feedback
            INNER JOIN haulage_freight_rates rate
            ON rate.id = feedback.haulage_freight_rate_id 
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]    

            result = Parallel(n_jobs=4)(delayed(delay_updation_feedback)(row, columns) for row in result.fetchall())
            cur.close()
    conn.close()
    print('haulage Freight Rate Feedbacks Done')
    return all_result
    # except Exception as e:
    #     return all_result

def delay_updation_feedback(row,columns):
    param = dict(zip(columns, row))
    # trailer_type = TextField(null=True)
    # haulage_type = TextField(null=True)
    # trip_type = TextField(null=True)
    obj = HaulageFreightRateFeedback(**param)
    print('done')
    set_locations(obj)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return


######################### Haulage freight rate request Migration ##################################################


def haulage_freight_rate_requests_migration():
    from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest
    all_result =[]
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql_query = """
            SELECT * FROM haulage_freight_rate_requests 
            """
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
    obj = HaulageFreightRateRequest(**param)
    print('here')
    set_locations(obj)
    get_multiple_service_objects(obj)
    obj.save(force_insert = True)
    return


def haulage_freight_rate_bulk_operations_migration():
    from services.haulage_freight_rate.models.haulage_freight_rate_bulk_operation import HaulageFreightRateBulkOperation
    all_result = []
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
                
            sql_query = """
            SELECT * FROM haulage_freight_rate_bulk_operations
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]    
            result = Parallel(n_jobs=4)(delayed(delay_updation_bulk_operation)(row, columns) for row in result.fetchall())
            cur.close()
    conn.close()
    print('haulage Freight Rate Bulk Operations Done')
    return all_result

def delay_updation_bulk_operation(row,columns):
    param = dict(zip(columns, row))
    obj = HaulageFreightRateBulkOperation(**param)
    obj.save(force_insert = True)
    return
    
def haulage_freight_rate_migration():
    all_result=[]
    # procured_ids_path = "procured_by_sourced_by_rates.json"
    # with open(procured_ids_path, 'r') as file:
    #     procured_sourced_rates_dict = json.load(file)
    
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql_query = """
            select * from haulage_freight_rates where transport_modes_keyword = 'rail' limit 10000
            """
            cur.execute(sql_query,)
            result = cur
            columns = [col[0] for col in result.description]
            result = Parallel(n_jobs=4)(delayed(delay_updation_rate)(row, columns) for row in result.fetchall())  
            cur.close()
    conn.close()
    print('haulage Freight Rate Done')
    return all_result

def delay_updation_rate(row,columns):
    param = dict(zip(columns, row))
    try:
        obj = HaulageFreightRate(**param)
        # set_procured_sourced(obj,procured_sourced_dict)
        set_locations(obj)
        get_multiple_service_objects(obj)
        
        obj.save(force_insert = True)
    except:
        print('ss')
    return


def set_locations(rate):
    ids = []
    if hasattr(rate, 'origin_location_id') and rate.origin_location_id:
        ids.append(str(rate.origin_location_id))
    if hasattr(rate, 'destination_location_id') and rate.destination_location_id:
        ids.append(str(rate.destination_location_id))

    obj = {'filters':{"id": ids}}
    locations_response = maps.list_locations(obj)
    locations = []
    if 'list' in locations_response:
        locations = locations_response["list"]

    for location in locations:
        if hasattr(rate, 'origin_location_id') and str(rate.origin_location_id) == str(location['id']):
            rate.origin_location = get_required_location_data(location)
        if hasattr(rate, 'destination_location_id') and str(rate.destination_location_id) == str(location['id']):
            rate.destination_location = get_required_location_data(location)
          
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

# def spot_search_data(rate):
#     from micro_services.client import spot_search
#     obj = {'filters':{"id": rate.source_id}}
#     spot_search_data = spot_search.list_spot_searches(obj)
#     spot_searches = []
#     if 'list' in spot_search_data:
#         spot_searches = spot_search_data["list"]

#     for search in spot_searches:
#         if hasattr(rate, 'source_id') and str(rate.source_id) == str(search['id']):
#             rate.spot_search = get_required_spot_search_data(search)

# def get_required_spot_search_data(search):
#     return {
#         'id' : search.get('id'), 
#         'importer_exporter_id' : search.get('importer_exporter_id'), 
#         'importer_exporter' :search.get('importer_exporter'), 
#         'service_details' :search.get('service_details')
#     }

def func_in_parallel(row, columns, procured_sourced_dict, model_name):
    param = dict(zip(columns, row))
    
    obj = HaulageFreightRate(**final_params)
    set_procured_sourced(obj,procured_sourced_dict)
    # set_location_data(obj,loc_dict)
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
                if model == 'haulage_freight_rate_local':
                    sql_query = "select object_id, procured_by_id, sourced_by_id from haulage_freight_rate_audits where object_type = 'HaulageFreightRateLocal'"
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
        if model == 'haulage_freight_rate_local':
            file_path = "procured_by_sourced_by_locals.json"
        else:
            file_path = "procured_by_sourced_by_cfs.json"
        with open(file_path, 'w') as file:
            json.dump(procured_sourced_dict, file)
    except Exception as e:
        return None

    
    
def run_migration():
    # haulage_freight_rate_feedback_migration()
    # haulage_freight_rate_requests_migration()
    # haulage_freight_rate_audits_migration()
    # haulage_freight_rate_bulk_operations_migration()
    # haulage_freight_rate_migration()
    print('Procured by Sourced by Data done')
