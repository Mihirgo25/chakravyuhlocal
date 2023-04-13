from currency_converter import CurrencyConverter
from datetime import date

currency = CurrencyConverter()


def get_money_exchange_for_fcl_fallback(from_currency, to_currency, price):
    return {"price": currency.convert(price, from_currency, to_currency)}
