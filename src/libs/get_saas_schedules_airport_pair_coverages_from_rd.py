from database.db_session import rd
import json

def get_key(origin_airport_id, destination_airport_id):
    return f"{origin_airport_id}:{destination_airport_id}"

def get_saas_schedules_airport_pair_coverages_from_rd(data):
    try:
        serviceable_airline_ids = rd.get(get_key(data.get('origin_airport_id'),data.get('destination_airport_id')))
        if serviceable_airline_ids:
            return json.loads(serviceable_airline_ids)
        return None
    except:
        return None

def set_saas_schedules_airport_pair_coverages_to_rd(origin_airport_id, destination_airport_id, serviceable_airline_ids):
    if rd and serviceable_airline_ids:
        key = get_key(origin_airport_id, destination_airport_id)
        rd.set(key, json.dumps(serviceable_airline_ids))
        rd.expire(key, 300)
