from datetime import date
from currency_converter import CurrencyConverter
from libs.cached_money_exchange import set_money_exchange_to_rd

currency = CurrencyConverter()


def get_money_exchange_for_fcl_fallback(from_currency, to_currency, price):
    from micro_services.client import common
    resp = common.get_all_exchange_rates({'base_currency':to_currency})
    
    if isinstance(resp, dict) and resp.get('cogofx_currencies', {}).get(from_currency):
        price = float(price)
        exchange_rate = resp['cogofx_currencies'][from_currency]
        set_money_exchange_to_rd(from_currency, to_currency, exchange_rate)
        return {'price': price * float(exchange_rate)}

    return {"price": currency.convert(price, from_currency, to_currency)}
