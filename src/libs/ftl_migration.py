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
from services.ftl_freight_rate.models.ftl_freight_rate_bulk_operation import FtlFreightRateBulkOperation
from libs.migration import delayed_func
import json
from fastapi.encoders import jsonable_encoder
import pandas as pd
from configs.definitions import ROOT_DIR
from psycopg2 import sql


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