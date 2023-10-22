from database.db_session import rd
import json

def get_charge_key(charge_name):
    return f"charge:{charge_name}"

def get_charge_from_rd(charge_name):
    try:
        charge_data = rd.get(get_charge_key(charge_name))
        if charge_data:
            return json.loads(charge_data)  
        return None
    except:
        return None

def set_charge_to_rd(charge_name, charge_data):
    if rd and charge_data:
        key = get_charge_key(charge_name)
        rd.set(key, json.dumps(charge_data)) 
        rd.expire(key, 86400)
