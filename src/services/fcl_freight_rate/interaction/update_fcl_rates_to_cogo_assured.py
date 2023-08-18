from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE, DEFAULT_SERVICE_PROVIDER_ID, DEFAULT_SHIPPING_LINE_ID, DEFAULT_SOURCED_BY_ID
from configs.env import DEFAULT_USER_ID
from datetime import timedelta, datetime
from services.fcl_freight_rate.interaction.get_suggested_cogo_assured_fcl_freight_rates import get_suggested_cogo_assured_fcl_freight_rates
from micro_services.client import common
import statistics

def get_assured_rate(all_prices):
    prices = []
    for price_curr in all_prices:
        if price_curr["currency"] != "USD":
            price_curr["price"] = common.get_money_exchange_for_fcl( {"price": price_curr["price"], "from_currency": price_curr["currency"], "to_currency": "USD"} )["price"]
        
        prices.append(int(price_curr["price"]))
    prices = sorted(prices)
    if len(prices) > 5:
        prices = prices[:5]
    median_price = statistics.median(prices)
    return int(median_price)

def update_fcl_rates_to_cogo_assured(param):
    freight_rates = list(FclFreightRate.select(FclFreightRate.validities).where(
        FclFreightRate.mode.not_in(['predicted', 'cluster_extension']),
        FclFreightRate.origin_port_id == param["origin_port_id"],
        FclFreightRate.origin_main_port_id == param["origin_main_port_id"],
        FclFreightRate.destination_port_id == param["destination_port_id"],
        FclFreightRate.destination_main_port_id == param["destination_main_port_id"],
        FclFreightRate.container_size == param["container_size"],
        FclFreightRate.container_type == param["container_type"],
        FclFreightRate.commodity == param["commodity"],
        FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
        ~ FclFreightRate.rate_not_available_entry,
        FclFreightRate.last_rate_available_date >= datetime.now().date()
    ).dicts())
    
    all_prices = []

    for val in freight_rates:
        for validity in val.values():
            for each_validity in validity:
                if datetime.fromisoformat(each_validity['validity_end']).date() >= datetime.now().date():
                    all_prices.append({
                        "price": each_validity["price"],
                        "currency":each_validity["currency"]
                    })
    assured_price = 0
    if all_prices:            
        assured_price = get_assured_rate(all_prices)

    if assured_price <= 0:
        return True
    
    rate_param = {
        "container_size": param["container_size"],
        "price": assured_price,
        "currency": "USD"
    }
    
    validities = get_suggested_cogo_assured_fcl_freight_rates(rate_param)["data"]["validities"]
    
    create_param = {
        "origin_port_id": param["origin_port_id"],
        "origin_main_port_id": param["origin_main_port_id"],
        "destination_port_id": param["destination_port_id"],
        "destination_main_port_id": param["destination_main_port_id"],
        "container_size": param["container_size"],
        "container_type": param["container_type"],
        "commodity": param["commodity"],
        "validities": validities,
        "service_provider_id": DEFAULT_SERVICE_PROVIDER_ID,
        "shipping_line_id": DEFAULT_SHIPPING_LINE_ID,
        "sourced_by_id": DEFAULT_SOURCED_BY_ID,
        "procured_by_id": DEFAULT_USER_ID,
        "performed_by_id": DEFAULT_USER_ID,
        "rate_type": "cogo_assured",
        "mode": "manual",
        "validity_start": validities[0]["validity_start"],
        "validity_end": validities[-1]["validity_end"],
        "available_inventory": 100,
        "used_inventory": 0,
        "shipment_count": 0,
        "volume_count": 0
    }
    # id = create_fcl_freight_rate_data(create_param)
    from celery_worker import create_fcl_freight_rate_delay
    create_fcl_freight_rate_delay.apply_async(kwargs={ 'request':create_param }, queue='fcl_freight_rate')
    return True