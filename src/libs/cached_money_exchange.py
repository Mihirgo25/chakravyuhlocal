from database.db_session import rd


def get_key(data):
    return f"{data.get('from_currency')}:{data.get('to_currency')}:{data.get('organization_id', '')}"

def get_money_exchange_from_rd(data):
    try:
        conversion_rate = rd.get(get_key(data))
        return float(conversion_rate) * float(data.get('price'))
    except:
        return None


def set_money_exchange_to_rd(data, exchange_rate):
    if rd and exchange_rate:
        key = get_key(data)
        rd.set(key, exchange_rate)
        rd.expire(key, 3600)
