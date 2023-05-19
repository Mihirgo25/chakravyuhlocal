import psycopg2
from configs.env import *
import sentry_sdk
from database.db_session import rd
import json

def get_connection():
    conn = psycopg2.connect(
    database=RAILS_DATABASE_NAME,
    host=RAILS_DATABASE_HOST,
    user=RAILS_DATABASE_USER,
    password=RAILS_DATABASE_PASSWORD,
    port=RAILS_DATABASE_PORT,
    )
    return conn


def get_shipping_line(id=None, short_name=None):
    all_result = []
    try:
        newconnection = get_connection()  
        with newconnection:
            with newconnection.cursor() as cur:
                if short_name:
                    sql = 'select operators.id, operators.business_name, operators.short_name, operators.logo_url,operators.operator_type, operators.status from operators where operators.short_name = %s and operators.status = %s and operators.operator_type = %s'
                    cur.execute(sql, (short_name,'active','shipping_line',))
                else:
                    if not isinstance(id, list):
                        id = (id,)
                    else:
                        id = tuple(id)
                    sql = 'select operators.id, operators.business_name, operators.short_name, operators.logo_url,operators.operator_type, operators.status from operators where operators.id in %s'
                    cur.execute(sql, (id,))

                result = cur.fetchall()

                for res in result:
                    all_result.append(
                        {
                            "id": str(res[0]),
                            "business_name": res[1],
                            "short_name": res[2],
                            "logo_url": res[3],
                            "operator_type": res[4],
                            "status": res[5]
                        }
                    )
                cur.close()
        newconnection.close()
        return all_result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return all_result

def get_organization(id=None, short_name=None):
    all_result = []
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                if short_name:
                    sql = 'select organizations.id, organizations.business_name, organizations.short_name,organizations.category_types, organizations.account_type, organizations.kyc_status, organizations.status from organizations where organizations.short_name = %s and status = %s and account_type = %s'
                    cur.execute(sql, (short_name,'active','importer_exporter',))
                else:
                    if not isinstance(id, list):
                        id = (id,)
                    else:
                        id = tuple(id)
                    sql = 'select organizations.id, organizations.business_name, organizations.short_name,organizations.category_types, organizations.account_type, organizations.kyc_status, organizations.status from organizations where organizations.id in %s'
                    cur.execute(sql, (id,))

                result = cur.fetchall()

                for res in result:
                    all_result.append(
                        {
                            "id": str(res[0]),
                            "business_name": res[1],
                            "short_name": res[2],
                            "category_types":res[3],
                            "account_type":res[4],
                            "kyc_status" : res[5],
                            "status":res[6]
                        }
                    )
                cur.close()
        conn.close()
        return all_result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return all_result

def get_user(id):
    all_result = []
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                if not isinstance(id, list):
                    id = (id,)
                else:
                    id = tuple(id)
                sql = 'select users.id, users.name, users.email, users.mobile_number_eformat from users where users.id in %s'
                cur.execute(sql, (id,))
                result = cur.fetchall()
                for res in result:
                    all_result.append(
                        {
                            "id": str(res[0]),
                            "name": res[1],
                            "email": res[2],
                            "mobile_number_eformat":res[3]
                        }
                    )
                cur.close()
        conn.close()
        return all_result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return all_result

def get_eligible_orgs(service):
    all_result = []
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur = conn.cursor()
                sql = 'select organization_services.organization_id from organization_services where status = %s and service = %s'
                cur.execute(sql, ('active', service,))
                result = cur.fetchall()
                for res in result:
                    all_result.append(str(res[0]))
                cur.close()
        conn.close()
        return all_result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return all_result
    

def get_partner_user_experties(service, partner_user_id):
    all_result = []
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                sql = 'select partner_user_expertises.origin_location_id, partner_user_expertises.destination_location_id, partner_user_expertises.location_id, partner_user_expertises.trade_type from partner_user_expertises where status = %s and service_type = %s and partner_user_id = %s'
                cur.execute(sql, ('active', service, partner_user_id,))
                result = cur.fetchall()

                for res in result:
                    new_obj = {
                        "origin_location_id": str(res[0]),
                        "destination_location_id": str(res[1]),
                        "location_id": str(res[2]),
                        "trade_type": str(res[3]),
                    }
                    all_result.append(new_obj)
                cur.close()
        conn.close()
        return all_result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return all_result

def get_partner_users_by_expertise(service, origin_location_ids = None, destination_location_ids = None, location_ids = None, trade_type = None):
    all_result = []
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                if origin_location_ids and destination_location_ids:
                    origin_location_ids = tuple(origin_location_ids)
                    destination_location_ids = tuple(destination_location_ids)
                    sql = 'select partner_user_expertises.partner_user_id, partner_user_expertises.origin_location_id, partner_user_expertises.destination_location_id, partner_user_expertises.location_id, partner_user_expertises.trade_type from partner_user_expertises where status = %s and service_type = %s and origin_location_id IN %s and destination_location_id IN %s'
                    cur.execute(sql, ('active', service, origin_location_ids, destination_location_ids,))
                else:
                    location_ids = tuple(location_ids)
                    sql = 'select partner_user_expertises.partner_user_id, partner_user_expertises.origin_location_id, partner_user_expertises.destination_location_id, partner_user_expertises.location_id, partner_user_expertises.trade_type from partner_user_expertises where status = %s and service_type = %s and partner_user_id = %s and location_id IN %s and trade_type = %s'
                    cur.execute(sql, ('active', service, location_ids, trade_type,))

                result = cur.fetchall()
                for res in result:
                    new_obj = {
                        "partner_user_id": str(res[0]),
                        "origin_location_id": str(res[1]),
                        "destination_location_id": str(res[2]),
                        "location_id": str(res[3]),
                        "trade_type": str(res[4]),
                    }
                    all_result.append(new_obj)
                cur.close()
        conn.close()
        return all_result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return all_result

def get_organization_stakeholders(stakeholder_type, stakeholder_id):
    org_ids = []
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                sql = 'select organization_stakeholders.organization_id from organization_stakeholders where status = %s and stakeholder_type = %s and stakeholder_id = %s'
                cur.execute(sql, ('active', stakeholder_type, stakeholder_id,))
                result = cur.fetchall()

                for res in result:
                    org_ids.append(str(res[0]))
                cur.close()
        conn.close()
        return org_ids
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return org_ids

def get_partner_users(ids, status = 'active'):
    if not ids:
        return []
    all_result = []
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                ids = tuple(ids)
                sql = 'select partner_users.user_id, partner_users.id from partner_users where status = %s and id IN %s'
                cur.execute(sql, ( status, ids,))
                result = cur.fetchall()
                for res in result:
                    new_obj = {
                        "user_id": str(res[0]),
                        "id": str(res[1]),
                    }
                    all_result.append(new_obj)
                cur.close()
        conn.close()
        return all_result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return all_result

def get_organization_service_experties(service, supply_agent_id, account_type = 'supply_agent'):
    all_result = []
    try:
        if account_type == 'supply_agent':
            org_ids = get_organization_stakeholders('supply_agent', supply_agent_id)
        else:
            org_ids = [supply_agent_id]
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                if len(org_ids) == 0:
                    return []
                org_ids_tuple = tuple(org_ids)
                sql = 'select organization_service_expertises.origin_location_id, organization_service_expertises.destination_location_id, organization_service_expertises.location_id, organization_service_expertises.trade_type, organization_service_expertises.organization_id from organization_service_expertises join organization_services on organization_service_expertises.service_id = organization_services.id where organization_service_expertises.status = %s and organization_services.service = %s and organization_service_expertises.organization_id IN %s'
                cur.execute(sql, ('active', service, org_ids_tuple,))
                result = cur.fetchall()

                for res in result:
                    new_obj = {
                        "origin_location_id": str(res[0]),
                        "destination_location_id": str(res[1]),
                        "location_id": str(res[2]),
                        "trade_type": str(res[3]),
                        "organization_id": str(res[4])
                    }
                    all_result.append(new_obj)
                cur.close()
        conn.close()
        return all_result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return all_result

def get_ff_mlo():
    ff_mlo = rd.get('ff_mlo')
    if ff_mlo:
        return json.loads(ff_mlo)
    result = []
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                sql = 'select organizations.id from organizations where organizations.account_type = %s and organizations.status = %s and ARRAY[%s, %s]::varchar[] && organizations.category_types and not (%s = ANY(organizations.category_types))'
                cur.execute(sql, ('service_provider', 'active', 'shipping_line', 'freight_forwarder', 'nvocc',))
                result = cur.fetchall()
                result = [str(x[0]) for x in result]
                cur.close()
        conn.close()
        rd.set('ff_mlo', json.dumps(result), ex=86400)
        return result
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return result

from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate
import datetime

def migrate_cogo_assured_fcl_to_rms_table():
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                chunk_size = 500
                status = 'active'
                sql = 'select count(*) from cogo_assured_fcl_freight_rates left join cogo_assured_rates on cogo_assured_fcl_freight_rates.cogo_assured_rate_id = cogo_assured_rates.id where cogo_assured_rates.status = %s'
                cur.execute(sql, ( status,))
                result = cur.fetchall()
                total_rows = result
                total_rows = 500
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
                        result['performed_by_id'] = '039a0141-e6f3-43b0-9c51-144b22b9fc84'
                        result['procured_by_id'] = 'd862bb07-02fb-4adc-ae20-d6e0bda7b9c1'
                        result['sourced_by_id'] = '7f6f97fd-c17b-4760-a09f-d70b6ad963e8'
                        result['shipment_count'] = 0
                        result['volume_count'] = 0
                        try:
                            id = create_fcl_freight_rate(result)
                        except Exception as e:
                            id = 0
                        print(id)
                cur.close()
        conn.close()
        return {"message": "Created rates in fcl with tag cogo_assured"}
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return e