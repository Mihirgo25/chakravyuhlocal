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


def get_shipping_line(id=None, short_name=None, operator_type='shipping_line'):
    all_result = []
    try:
        newconnection = get_connection()  
        with newconnection:
            with newconnection.cursor() as cur:
                if short_name:
                    sql = 'select operators.id, operators.business_name, operators.short_name, operators.logo_url,operators.operator_type, operators.status from operators where operators.short_name = %s and operators.status = %s and operators.operator_type = %s'
                    cur.execute(sql, (short_name,'active',operator_type,))
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

def get_past_invoices(origin_location_id,destination_location_id,location_type):
        all_results =[]
        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cur:
                     
                    sql_query = """
                        select shipment_air_freight_services.origin_airport_id as origin_airport_id, 
                        shipment_air_freight_services.origin_country_id as origin_country_id, 
                        shipment_air_freight_services.destination_airport_id as destination_airport_id,
                        shipment_air_freight_services.destination_country_id as destination_country_id,
                        shipment_air_freight_services.operation_type, shipment_air_freight_services.weight,shipment_air_freight_services.commodity,
                        line_item ->> 'price' as price, line_item ->> 'currency' as currency,shipment_air_freight_services.airline_id from shipment_collection_parties
                        inner join shipment_air_freight_services on shipment_collection_parties.shipment_id = shipment_air_freight_services.shipment_id
                        cross join jsonb_array_elements(line_items) as line_item
                        where shipment_collection_parties.invoice_date > date_trunc('MONTH',CURRENT_DATE - INTERVAL '3 months')::DATE
                        and shipment_air_freight_services.origin_{}_id = %s
                        and shipment_air_freight_services.destination_{}_id = %s
                        and shipment_collection_parties.status in ('locked', 'coe_approved','finance_rejected') and  line_item ->> 'code' = 'BAS' and
                        invoice_type in ('purchase_invoice', 'proforma_invoice')
                        """.format(location_type,location_type)
                    cur.execute(sql_query,(origin_location_id,destination_location_id))
                    result = cur.fetchall()
                    cur.close()

                for res in result:

                    new_obj = {
                        "origin_airport_id": str(res[0]),
                        "origin_country_id": str(res[1]),
                        "destination_airport_id": str(res[2]),
                        "destination_country_id": str(res[3]),
                        "operation_type":res[4],
                        "weight":res[5],
                        "commodity":res[6],
                        "price":str(res[7]),
                        "currency":str(res[8]),
                        "airline_id":str(res[9])
                    }

                    all_results.append(new_obj)
                    cur.close()
            conn.close()
            return all_results
        except Exception as e:
            # sentry_sdk.capture_exception(e)
            return result
        
def get_invoices():
        all_result =[]
        try:
            conn = get_connection()
            with conn:
                with conn.cursor() as cur:
                     
                    sql_query = """
                        select shipment_air_freight_services.origin_airport_id as origin_airport_id, 
                        shipment_air_freight_services.origin_country_id as origin_country_id, 
                        shipment_air_freight_services.destination_airport_id as destination_airport_id,
                        shipment_air_freight_services.destination_country_id as destination_country_id,
                        shipment_air_freight_services.operation_type, shipment_air_freight_services.weight,shipment_air_freight_services.commodity,
                        line_item ->> 'price' as price, line_item ->> 'currency' as currency,
                        shipment_air_freight_services.airline_id
                        from shipment_collection_parties
                        inner join shipment_air_freight_services on shipment_collection_parties.shipment_id = shipment_air_freight_services.shipment_id
                        cross join jsonb_array_elements(line_items) as line_item
                        where 
                         shipment_collection_parties.status in ('locked', 'coe_approved','finance_rejected') and  line_item ->> 'code' = 'BAS' and
                        invoice_type in ('purchase_invoice', 'proforma_invoice')
                        """
                    cur.execute(sql_query)
                    result = cur.fetchall()

                for res in result:

                    new_obj = {
                        "origin_airport_id": str(res[0]),
                        "origin_country_id": str(res[1]),
                        "destination_airport_id": str(res[2]),
                        "destination_country_id": str(res[3]),
                        "operation_type":res[4],
                        "weight":res[5],
                        "commodity":res[6],
                        "price":str(res[7]),
                        "currency":str(res[8]),
                        "airline_id":str(res[9])
                    }

                    all_result.append(new_obj)
                    cur.close()
            conn.close()
            return all_result
        except Exception as e:
            print(e)
            # sentry_sdk.capture_exception(e)
            return all_result



                    
            
