from database.db_session import rd


def get_key(from_currency, to_currency):
    return f"{from_currency}:{to_currency}"

def get_money_exchange_from_rd(data):
    try:
        conversion_rate = rd.get(get_key(data.get('from_currency'),data.get('to_currency')))
        return float(conversion_rate) * float(data.get('price'))
    except:
        return None


def set_money_exchange_to_rd(from_currency, to_currency, exchange_rate):
    if rd and exchange_rate:
        key = get_key(from_currency, to_currency)
        rd.set(key, exchange_rate)
        rd.expire(key, 3600)
