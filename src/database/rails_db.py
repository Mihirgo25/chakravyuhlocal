import psycopg2
from configs.env import *

conn = psycopg2.connect(
    database=RAILS_DATABASE_NAME,
    host=RAILS_DATABASE_HOST,
    user=RAILS_DATABASE_USER,
    password=RAILS_DATABASE_PASSWORD,
    port=RAILS_DATABASE_PORT
    )

print("connection successfull")

cur = conn.cursor()

def get_shipping_line(id):
    if not isinstance(id, list):
        id = (id,)
    else:
        id = tuple(id)
    sql = 'select operators.id, operators.business_name, operators.short_name, operators.logo_url from operators where operators.id in %s'
    cur.execute(sql, (id,))
    result = cur.fetchall()
    all_result = []
    for res in result:
        all_result.append(
            {
                "id": res[0],
                "business_name": res[1],
                "short_name": res[2],
                "logo_url": res[3]
            }
        )
    cur.close()
    return all_result
    
def get_service_provider(id):
    if not isinstance(id, list):
        id = (id,)
    else:
        id = tuple(id)
    sql = 'select organizations.id, organizations.business_name, organizations.short_name from organizations where organizations.id in %s'
    cur.execute(sql, (id,))
    result = cur.fetchall()
    all_result = []
    for res in result:
        all_result.append(
            {
                "id": res[0],
                "business_name": res[1],
                "short_name": res[2]
            }
        )
    cur.close()
    return all_result

def get_user(id):
    if not isinstance(id, list):
        id = (id,)
    else:
        id = tuple(id)
    sql = 'select users.id, users.name, users.email from users where users.id in %s'
    cur.execute(sql, (id,))
    result = cur.fetchall()
    all_result = []
    for res in result:
        all_result.append(
            {
                "id": res[0],
                "name": res[1],
                "email": res[2]
            }
        )
    cur.close()
    return all_result

    
    