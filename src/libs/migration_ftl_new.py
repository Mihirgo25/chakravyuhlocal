from configs.env import *
import json
from micro_services.client import maps
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from database.rails_db import get_connection
from joblib import delayed, Parallel, cpu_count
from services.ftl_freight_rate.models.ftl_freight_rate_feedback import FtlFreightRateFeedback
from services.ftl_freight_rate.models.ftl_freight_rate_request import FtlFreightRateRequest
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from libs.migration import delayed_func
import json
from fastapi.encoders import jsonable_encoder
import pandas as pd
from configs.definitions import ROOT_DIR
from psycopg2 import sql

def get_count(table_name):
    conn = get_connection()
    with conn:
        with conn.cursor() as cur: 
            cur.execute(sql.SQL('SELECT count(id) from {table}').format(table=sql.Identifier(table_name)))
            result = cur
            count = result.fetchall()
            cur.close()
    conn.close()
    return count

def set_locations(rate):
    ids = []
    if hasattr(rate, 'origin_location_id') and rate.origin_location_id:
        ids.append(str(rate.origin_location_id))
    if hasattr(rate, 'destination_location_id') and rate.destination_location_id:
        ids.append(str(rate.destination_location_id))

    locations_response = maps.list_locations({'filters':{"id": ids}, 'includes': {'id': True, 'name': True, 'type': True, 'is_icd': True, 'cluster_id': True, 'city_id': True, 'country_id':True, 'country_code': True}})
    locations = []
    locations = locations_response.get("list")
    for location in locations:
        if hasattr(rate, 'origin_location_id') and str(rate.origin_location_id) == str(location['id']):
            rate.origin_location = get_required_location_data(location)
        if hasattr(rate, 'destination_location_id') and str(rate.destination_location_id) == str(location['id']):
            rate.destination_location = get_required_location_data(location)
          
def get_required_location_data(location):
    loc_data =loc_data = {
          "id": location["id"],
          "name": location["name"],
          "is_icd": location["is_icd"],
          "type": location["type"],
          "cluster_id": location["cluster_id"],
          "city_id": location["city_id"],
          "country_id": location["country_id"],
          "country_code": location["country_code"]
        }
    return loc_data


###########################  ftl freight rate requests ##################################

def get_request_in_batches(table_name, OFFSET):
    limit = 2000
    conn = get_connection()
    results = {}
    columns = None
    with conn:
        with conn.cursor() as cur: 
            cur.execute(sql.SQL('SELECT * from {table} order by created_at desc OFFSET %s LIMIT %s ;').format(table=sql.Identifier(table_name)), [OFFSET, limit])
            result = cur
            if not columns:
                    columns = [col[0] for col in result.description]
            result = cur
            results = result.fetchall()
            cur.close()
    conn.close()
    return  columns, results


def create_ftl_request_rates():
    import uuid
    i,j = 0, 0
    count1 = get_count('ftl_freight_rate_requests')[0][0]
    print(count1)
    complete=0
    while i<count1:
        columns, resulta = get_request_in_batches('ftl_freight_rate_requests', i)
        print(len(resulta))
        for result in resulta:
            param = dict(zip(columns, result))
            print('done')
            complete+=1
            print(complete, (count1))
            if FtlFreightRateRequest.select().where(FtlFreightRateRequest.serial_id==param['serial_id']):
                continue
            obj = FtlFreightRateRequest(**param)
            get_multiple_service_objects(obj)
            set_locations(obj)
            obj.save(force_insert = True)
            
        i+=2000
    print('Migration done')

###########################  ftl freight rate audits ##################################

def get_rates_in_batches(table_name, OFFSET):
    limit = 2000
    conn = get_connection()
    results = {}
    columns = None
    with conn:
        with conn.cursor() as cur: 
            cur.execute(sql.SQL('SELECT * from {table} order by created_at desc OFFSET %s LIMIT %s ;').format(table=sql.Identifier(table_name)), [OFFSET, limit])
            result = cur
            if not columns:
                    columns = [col[0] for col in result.description]
            result = cur
            results = result.fetchall()
            cur.close()
    conn.close()
    return  columns, results

def create_ftl_freight_rate_audits():
    i = 0
    count = get_count('ftl_freight_rate_audits')[0][0]
    while i<count:
        columns, resulta = get_rates_in_batches('ftl_freight_rate_audits', i)
        for result in resulta:
            param = dict(zip(columns, result))
            obj = FtlFreightRateAudit(**param)
            try:
                obj.save(force_insert = True)
            except:
                print('repeat')
        print(i)
        i+=2000
    print('Migration done')

###########################  ftl freight rate feedbacks ##################################

def get_feedback_in_batches(table_name, OFFSET):
    limit = 2000
    conn = get_connection()
    results = {}
    columns = None
    with conn:
        with conn.cursor() as cur: 
            cur.execute(sql.SQL('SELECT * from {table} order by created_at desc OFFSET %s LIMIT %s ;').format(table=sql.Identifier(table_name)), [OFFSET, limit])
            result = cur
            if not columns:
                    columns = [col[0] for col in result.description]
            result = cur
            results = result.fetchall()
            cur.close()
    conn.close()
    return  columns, results

def create_ftl_feedback_rates():
    import json
    data = None
    json_file = open(os.path.join(ROOT_DIR, 'libs/ftl_freight_rate_feedback_extra_columns_mapping.json'))
    data = json.load(json_file)

    extra_columns_dic={}
    for row in data:
        extra_columns_dic[row['id']]=row
    not_present = 0
    import uuid
    i,j = 0, 0
    count1 = get_count('ftl_freight_rate_feedbacks')[0][0]
    print(count1)
    
    complete=0
    while i<count1:
        columns, resulta = get_feedback_in_batches('ftl_freight_rate_feedbacks', i)
        print(len(resulta))
        for result in resulta:
            param = dict(zip(columns, result))
            ftl_freight_id = str(param['ftl_freight_rate_id'])

            if ftl_freight_id in extra_columns_dic:
                for key, val in extra_columns_dic[ftl_freight_id].items():
                    if key not in ['id']:
                        param[key] = val
            else:
                not_present+=1
            print('done')
            complete+=1
            print(complete, (count1))
            obj = FtlFreightRateFeedback(**param)
            set_locations(obj)
            obj.save(force_insert = True)

        i+=2000
    print('Migration done: ', not_present)






    


                
