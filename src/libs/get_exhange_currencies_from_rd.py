from database.db_session import rd
import json

def list_exchange_rate_currencies_key():
    return "exchange_rate_currencies"  

def list_exchange_rate_currencies_from_rd():
    try:
        currency_code = rd.get(list_exchange_rate_currencies_key())
        if currency_code:
            return json.loads(currency_code)
        return None
    except:
        return None

def set_exchange_rate_currencies_to_rd(currency_code):
    if rd and currency_code:
        key = list_exchange_rate_currencies_key()
        rd.set(key, json.dumps(currency_code))
        rd.expire(key, 86400)