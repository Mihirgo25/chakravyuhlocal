import psycopg2
from configs.env import *
conn = psycopg2.connect(
    database=RAILS_DATABASE_NAME,
    host=RAILS_DATABASE_HOST,
    user=RAILS_DATABASE_USER,
    password=RAILS_DATABASE_PASSWORD,
    port=RAILS_DATABASE_PORT
    )

print("connection successful")


def get_shipping_line(id):
    cur = conn.cursor()

    if not isinstance(id, list):
        id = (id,)
    else:
        id = tuple(id)
    sql = 'select operators.id, operators.business_name, operators.short_name, operators.logo_url,operators.operator_type, operators.status from operators where operators.id in %s'
    cur.execute(sql, (id,))
    result = cur.fetchall()
    all_result = []
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
    return all_result
    
def get_service_provider(id):
    cur = conn.cursor()

    if not isinstance(id, list):
        id = (id,)
    else:
        id = tuple(id)
    sql = 'select organizations.id, organizations.business_name, organizations.short_name,organizations.category_types, organizations.account_type, organizations.kyc_status, organizations.status from organizations where organizations.id in %s'
    cur.execute(sql, (id,))
    result = cur.fetchall()
    all_result = []
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
    return all_result

def get_user(id):
    cur = conn.cursor()

    if not isinstance(id, list):
        id = (id,)
    else:
        id = tuple(id)
    sql = 'select users.id, users.name, users.email, users.mobile_number_eformat from users where users.id in %s'
    cur.execute(sql, (id,))
    result = cur.fetchall()
    all_result = []
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
    return all_result

def get_eligible_orgs(service):
    cur = conn.cursor()
    sql = 'select organization_services.organization_id from organization_services where status = %s and service = %s'
    cur.execute(sql, ('active', service,))
    result = cur.fetchall()
    all_result = []
    for res in result:
        all_result.append(str(res[0]))
    cur.close()
    return all_result
    
def get_partner_user_experties(service, partner_user_id):
    cur = conn.cursor()
    sql = 'select partner_user_expertises.origin_location_id, partner_user_expertises.destination_location_id, partner_user_expertises.location_id, partner_user.trade_type from partner_user_expertises where status = %s and service = %s and partner_user_id = %s'
    cur.execute(sql, ('active', service, partner_user_id,))
    result = cur.fetchall()
    all_result = []
    for res in result:
        new_obj = {
            "origin_location_id": str(res[0]),
            "destination_location_id": str(res[1]),
            "location_id": str(res[2]),
            "trade_type": str(res[3]),
        }
        all_result.append(new_obj)
    cur.close()
    return all_result

def get_organization_stakeholders(stakeholder_type, stakeholder_id):
    cur = conn.cursor()
    sql = 'select organization_stakeholders.organization_id from organization_stakeholders where status = %s and stakeholder_type = %s and stakeholder_id = %s'
    cur.execute(sql, ('active', stakeholder_type, stakeholder_id,))
    result = cur.fetchall()
    org_ids = []
    for res in result:
        org_ids.append(str(res[0]))
    cur.close()
    return org_ids

def get_organization_service_experties(service, supply_agent_id):
    cur = conn.cursor()
    org_ids = get_organization_stakeholders('supply_agent', supply_agent_id)
    if len(org_ids) == 0:
        return []
    org_ids_tuple = tuple(org_ids)
    sql = 'select organization_service_expertises.origin_location_id, organization_service_expertises.destination_location_id, organization_service_expertises.location_id, organization_service_expertises.trade_type, organization_service_expertises.organization_id from organization_service_expertises where status = %s and service = %s and organization_id IN %s'
    cur.execute(sql, ('active', service, org_ids_tuple,))
    result = cur.fetchall()
    all_result = []
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
    return all_result