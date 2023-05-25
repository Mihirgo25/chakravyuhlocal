from database.rails_db import get_connection
import sentry_sdk
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate
import datetime
from configs.env import DEFAULT_USER_ID
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

def migrate_cogo_assured_fcl_to_rms_table():
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                chunk_size = 5000
                status = 'active'
                sql = 'select count(*) from cogo_assured_fcl_freight_rates left join cogo_assured_rates on cogo_assured_fcl_freight_rates.cogo_assured_rate_id = cogo_assured_rates.id where cogo_assured_rates.status = %s'
                cur.execute(sql, ( status,))
                result = cur.fetchall()
                total_rows = result[0][0]
                total_chunks = (total_rows // chunk_size) + 1
                for chunk in range(total_chunks):
                    offset = chunk * chunk_size
                    query = 'select cogo_assured_rates.origin_location_id as origin_port_id, cogo_assured_rates.origin_port_id as origin_main_port_id, cogo_assured_rates.destination_location_id as destination_port_id, cogo_assured_rates.destination_port_id as destination_main_port_id, cogo_assured_fcl_freight_rates.container_size as container_size, cogo_assured_fcl_freight_rates.container_type as container_type, cogo_assured_fcl_freight_rates.commodity as commodity, cogo_assured_fcl_freight_rates.shipping_line_id as shipping_line_id, cogo_assured_fcl_freight_rates.service_provider_id as service_provider_id, cogo_assured_fcl_freight_rates.validities as validities, cogo_assured_fcl_freight_rates.weight_limit as weight_limit, cogo_assured_fcl_freight_rates.origin_detention as origin_detention, cogo_assured_fcl_freight_rates.origin_demurrage as origin_demurrage, cogo_assured_fcl_freight_rates.origin_plugin as origin_plugin, cogo_assured_fcl_freight_rates.destination_detention as destination_detention, cogo_assured_fcl_freight_rates.destination_demurrage as destination_demurrage, cogo_assured_fcl_freight_rates.destination_plugin as destination_plugin, cogo_assured_fcl_freight_rates.inventory as available_inventory, cogo_assured_fcl_freight_rates.booked_inventory as used_inventory, cogo_assured_rates.value_props as value_props, cogo_assured_rates.terms_and_conditions as t_n_c, cogo_assured_fcl_freight_rates.validity_start, cogo_assured_fcl_freight_rates.validity_end from cogo_assured_fcl_freight_rates left join cogo_assured_rates on cogo_assured_fcl_freight_rates.cogo_assured_rate_id = cogo_assured_rates.id where cogo_assured_rates.status = %s limit %s offset %s'
                    cur.execute(query, ( status, chunk_size, offset,))
                    params = cur.fetchall()
                    for param in params:
                        result = {}
                        result['origin_port_id'] = param[0]
                        result['origin_main_port_id'] = param[1]
                        result['destination_port_id'] = param[2]
                        result['destination_main_port_id'] = param[3]
                        result['container_size'] = param[4]
                        result['container_type'] = param[5]
                        result['commodity'] = param[6]
                        result['shipping_line_id'] = param[7]
                        result['service_provider_id'] = param[8]
                        result['line_items'] = []
                        for validity in param[9]:
                            new_validity = {key: value for key,value in validity.items() if key != 'id'}
                            result['line_items'].append(new_validity)
                        if param[10]:
                            if param[10].get('free_limit') and param[10].get('free_limit') != 0:
                                result['weight_limit'] = None
                        else:
                            result['weight_limit'] = param[10] 
                        result['available_inventory'] = param[17]
                        result['used_inventory'] = param[18]
                        result['value_props'] = param[19]
                        result['t_n_c'] = param[20]
                        result['validity_start'] = param[21] if param[21] else datetime.datetime.now()
                        result['validity_end'] = param[22] if param[22] else datetime.datetime.now()
                        result['rate_type']='cogo_assured'
                        result['origin_local'] = {'line_items':[],'detention':param[11],'demurrage':param[12],'plugin':param[13]}
                        result['destination_local'] = {'line_items':[],'detention':param[14],'demurrage':param[15],'plugin':param[16]}
                        result['performed_by_id'] = DEFAULT_USER_ID
                        result['procured_by_id'] = DEFAULT_USER_ID
                        result['sourced_by_id'] = DEFAULT_USER_ID
                        result['shipment_count'] = 0
                        result['volume_count'] = 0
                        id = create_fcl_freight_rate(result)
                        print(id)
                cur.close()
        conn.close()
        return {"message": "Created rates in fcl with tag cogo_assured"}
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return e
    
def add_market_place_to_init_key():
    chunk_size = 5000  
    total_rows = FclFreightRate.select().count()
    total_chunks = (total_rows // chunk_size) + 1

    for chunk in range(total_chunks):
        offset = chunk * chunk_size
        subquery = FclFreightRate.select(FclFreightRate.id).where(FclFreightRate.rate_type == 'market_place').limit(chunk_size).offset(offset)
        query = FclFreightRate.update(init_key=FclFreightRate.init_key.concat(':market_place')).where(FclFreightRate.id.in_(subquery),FclFreightRate.init_key.endswith(':market_place') == False)
        print(query)
        query.execute()
    return {"message": "Market place added to init_key column for all rows."}