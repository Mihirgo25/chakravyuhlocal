import requests
from bs4 import BeautifulSoup
from micro_services.client import maps
from configs.haulage_freight_rate_constants import GLOBAL_FUEL_DATA_LINKS


def find_electricity_price():
    payload = {
        "customers": "2",
        "currency": "USD",
    }
    response = requests.post(GLOBAL_FUEL_DATA_LINKS[0], data=payload)
    soup = BeautifulSoup(response.content, "html.parser")
    div_element_price = soup.find("div", {"id": "graphic"})
    div_element_country = soup.find("div", {"id": "outsideLinks"})
    div_data = div_element_price.text
    div_data_country = div_element_country.text
    country = div_data.splitlines()
    filtered_price = [element for element in country if element]
    price = div_data_country.splitlines()
    filtered_country = [element for element in price if element]
    country_codes = []
    last_element = filtered_price.pop()
    for country in filtered_country:
        input = {"filters": {"q": country, "type": "country"}}
        try:
            locations_data = maps.list_locations(input)["list"][0]["country_code"]
            country_codes.append(locations_data)
        except:
            country_codes.append("US")
    price_country_mapping = {}
    for i in range(len(filtered_price)):
        price_country_mapping[country_codes[i]] = filtered_price[i]
    return price_country_mapping
