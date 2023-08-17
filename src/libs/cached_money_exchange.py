from database.db_session import rd


def get_key(from_currency, to_currency):
    return f"{from_currency}:{to_currency}"

def get_money_exchange_from_rd(data):
    try:
        per_unit_value = rd.get(get_key(data.get('from_currency'),data.get('to_currency')))
        return float(per_unit_value) * float(data.get('price'))
    except:
        return None


def set_money_exchange_to_rd(data):
    if rd and data.get('per_unit_value'):
        key = get_key(data.get('from_currency'), data.get('to_currency'))
        rd.set(key, data['per_unit_value'])
        rd.expire(key, 3600)
