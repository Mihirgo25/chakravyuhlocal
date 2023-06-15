
from configs.ftl_freight_rate_constants import USA_FUEL_DATA_LINK, INDIA_FUEL_DATA_LINKS, EUROPE_FUEL_DATA_LINK, CHINA_FUEL_DATA_LINKS
import requests
import time
import copy
from bs4 import BeautifulSoup
from micro_services.client import *
from services.ftl_freight_rate.models.fuel_data import FuelData
from services.ftl_freight_rate.interaction.create_fuel_data import create_fuel_data
from configs.global_constants import COUNTRY_CODES_MAPPING
import services.ftl_freight_rate.scheduler.fuel_scheduler as fuel_schedulers


def fuel_scheduler():
    list_of_countries = ["europe","india", "usa", "china"]

    for country in list_of_countries:
        list_fuel_data = getattr(
            fuel_schedulers, "get_scrapped_data_for_{}".format(country)
        )()
        process_fuel_data(list_fuel_data, country)
        time.sleep(5)

def process_fuel_data(list_fuel_data, country):
    batch_size = 50
    num_batches = len(list_fuel_data)  # batch_size
    if num_batches == 0:
        return
    for batch in range(num_batches):
        start_index = batch * batch_size
        end_index = (
            start_index + batch_size
            if start_index + batch_size <= num_batches
            else num_batches
        )
        country_code = COUNTRY_CODES_MAPPING[country]
        if start_index<end_index:
            for fuel_data in list_fuel_data[start_index:end_index]:
                input = {
                    "filters": (
                        {
                        "q": fuel_data["location_name"],
                        "type": ["city", "district", "pincode"]
                        if fuel_data["location_type"] == "city "
                        else fuel_data["location_type"],
                        "status": "active",
                        "country_code": country_code,
                    }
                    )
                }
                list_location_data = maps.list_locations(input)["list"]
                fuel_data_list = get_fuel_data_list(fuel_data, list_location_data)
                for fuel_data in fuel_data_list:
                    create_fuel_data(fuel_data)
        else:
            pass



def get_fuel_data_list(scrapped_fuel_data, list_location_data):
    list_data = []
    for location_data in list_location_data:
        fuel_data = {}
        fuel_data["location_id"] = location_data["id"]
        fuel_data["location_type"] = location_data["type"]
        for key, value in scrapped_fuel_data.items():
            if key not in ["id", "location_name"]:
                fuel_data[key] = value
        list_data.append(copy.deepcopy(fuel_data))
    return list_data


def get_scrapped_data_for_india():
    urls = INDIA_FUEL_DATA_LINKS
    fuel_data_for_india = []
    for url, data_set in urls.items():
        request = requests.get(url)
        scrapper = BeautifulSoup(request.text, "html")
        data = scrapper.find("div", {"class": data_set[0]})
        table_data = data.find_all("td")
        link_data = data.find_all("a")
        start = 1
        for location_fuel_details in link_data:
            location_name = location_fuel_details.text
            fuel_price = float(table_data[start].text.replace(" ₹/L", ""))
            fuel_data = {
                "location_type": data_set[2],
                "location_name": location_name,
                "fuel_type": data_set[1],
                "fuel_price": fuel_price,
                "currency": "INR",
                "fuel_unit": "Lt",
            }
            fuel_data_for_india.append(copy.deepcopy(fuel_data))
            start += 3
    return fuel_data_for_india


def get_scrapped_data_for_usa():
    url = USA_FUEL_DATA_LINK
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    html = response.content
    scrapper = BeautifulSoup(html, "html.parser")
    table_body = scrapper.find("tbody")
    table_list = table_body.findAll("td")
    fuel_data_for_usa = []
    start = 0
    while start < (len(table_list)):
        region_name = table_list[start].a.text
        region_name = region_name.replace("\n", "").replace(" ", "")
        fuel_data = {}
        fuel_data["location_name"] = region_name
        fuel_data["currency"] = "USD"
        fuel_data["fuel_unit"] = "gallon"
        fuel_data["location_type"] = "region"
        for fuel_type in ["petrol", "diesel"]:
            if fuel_type == "petrol":
                fuel_data["fuel_type"] = fuel_type
                fuel_data["fuel_price"] = (
                    table_list[start + 1].text.strip().replace("$", "")
                )
            else:
                fuel_data["fuel_type"] = fuel_type
                fuel_data["fuel_price"] = (
                    table_list[start + 4].text.strip().replace("$", "")
                )

            fuel_data_for_usa.append(copy.deepcopy(fuel_data))
        start += 5
    return fuel_data_for_usa

def get_scrapped_data_for_europe():
    url = EUROPE_FUEL_DATA_LINK
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find_all('table')[0]
    rows = table.find_all('tr')

    fuel_data_for_europe = []
    for row in rows:
        fuel_data = {}
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]
        if cols == []:
            continue

        for fuel_type in ["petrol", "diesel"]:
            fuel_data["currency"] = "EUR"
            fuel_data["fuel_unit"] = "Lt"
            fuel_data["location_type"] = "country"
            fuel_data["fuel_type"] = fuel_type

            if cols[0]=='Czechia':
                fuel_data['location_name'] = 'Czech Republic'
            elif cols[0]=='North Macedonia':
                fuel_data['location_name'] = 'Macedonia'
            else:
                fuel_data['location_name'] = cols[0]

            if fuel_type == 'petrol' and cols[1]!='–':
                fuel_data['fuel_price'] = cols[1]
            elif fuel_type == 'diesel' and cols[2]!='–':
                fuel_data['fuel_price'] = cols[2]
            else:
                continue

            fuel_data_for_europe.append(copy.deepcopy(fuel_data))
    return fuel_data_for_europe

def get_scrapped_data_for_china():
    url = CHINA_FUEL_DATA_LINKS
    response = requests.get(url)
    scrapper = BeautifulSoup(response.text, 'html.parser')
    table_body = scrapper.find('tbody')
    table_header = table_body.find('td').text
    diesel_price=float(table_header)

    fuel_data_for_china = []
    fuel_data = {}
    fuel_data["location_name"] = 'china'
    fuel_data["currency"] = "CNY"
    fuel_data["fuel_unit"] = "Lt"
    fuel_data["location_type"] = "country"
    fuel_data["fuel_type"] = 'diesel'
    fuel_data["fuel_price"] = diesel_price
    fuel_data_for_china.append(fuel_data)
    return fuel_data_for_china
