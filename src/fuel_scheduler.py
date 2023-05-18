from scheduler import scheduler
from schedule import every
from configs.ftl_freight_rate_constants import USA_FUEL_DATA_LINK,INDIA_FUEL_DATA_LINK
import json
import requests
import pdb
import time
import copy
from bs4 import BeautifulSoup
from micro_services.client import *
from services.ftl_freight_rate.models.fuel_data import FuelData
from services.ftl_freight_rate.interaction.create_fuel_data import create_fuel_data
import fuel_scheduler as fuel_scheduler


@scheduler.add(every().day.at("00:00"))
def fuel_scheduler():
    list_of_countries = ['india','usa']
    
    for country in list_of_countries:
        list_fuel_data = getattr(fuel_scheduler, "get_scrapped_data_for_{}".format(country))()
        
        process_fuel_data(list_fuel_data)
        time.sleep(1)
    

def process_fuel_data(list_fuel_data):
    batch_size = 50
    num_batches = len(list_fuel_data)  # batch_size
    if num_batches == 0:
        return
    print(num_batches)
    for batch in range(num_batches):
        start_index = batch * batch_size
        end_index = (
            start_index + batch_size
            if start_index + batch_size <= num_batches
            else num_batches
        )
        print(start_index," ",end_index)
        for fuel_data in list_fuel_data[start_index:end_index]:
            input = {
                "filters": json.dumps(
                    {
                        "q": fuel_data["location_name"],
                        "type": fuel_data["location_type"],
                        "status": "active",
                        "country_code": "IN",
                    }
                )
            }
            location_data = maps.list_locations(input)["list"]
            fuel_data_mapping = get_fuel_data_mapping(
                fuel_data, location_data
            )
            if fuel_data_mapping:
                create_fuel_data(fuel_data_mapping)

    
def get_fuel_data_mapping(fuel_data, location_data):
    final_data = {}
    if bool(location_data):
        fuel_data["location_id"] = location_data[0]["id"]
        for key, values in fuel_data.items():
            if key not in ["id", "location_name"]:
                final_data[key] = values
    return final_data


def get_scrapped_data_for_india():
    fuel_data_for_india = []
    print("india entered")
    fuel_types = ["petrol", "diesel"]
    location_types = {"state": ["_4", "region"], "city": ["_3", "city"]}

    for fuel_type in fuel_types:
        for location_type in location_types.keys():
            url = INDIA_FUEL_DATA_LINK+"{}-{}-wise".format(
                fuel_type, location_type
            )
            r = requests.get(url)
            df = BeautifulSoup(r.text, "lxml")
            div = df.find("div", {"id": fuel_type + location_types[location_type][0]})
            ul = div.find_all("ul")[1:]
            for x in ul:
                data = {}
                fuel_price = x.find("strong").text
                if check_fuel_price(fuel_price):
                    data["location_name"] = x.find("a").text
                    data["fuel_type"] = fuel_type
                    data["fuel_price"] = fuel_price
                    data["currency"] = "INR"
                    data["fuel_unit"] = "Lt"
                    data["location_type"] = location_types[location_type][1]
                    fuel_data_for_india.append(data)

    return fuel_data_for_india

def get_scrapped_data_for_usa():
    url= USA_FUEL_DATA_LINK
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    html = response.content
    scrapper = BeautifulSoup(html, 'html.parser')
    table_body = scrapper.find("tbody")
    table_list = table_body.findAll('td')
    fuel_data_for_usa = []
    start = 0
    while start < (len(table_list)):
        region_name = table_list[start].a.text
        region_name = region_name.replace('\n','').replace(' ','')
        fuel_data = {}
        fuel_data['location_name'] = region_name
        fuel_data["currency"]= "USD"
        fuel_data["fuel_unit"]= "gallon"
        fuel_data["location_type"]= "region"
        for fuel_type in ['petrol','diesel']:
            if fuel_type == 'petrol':
                fuel_data["fuel_type"] = fuel_type    
                fuel_data['fuel_price'] = table_list[start+1].text.replace(" ", "")            
            else:
                fuel_data["fuel_type"] = fuel_type    
                fuel_data['fuel_price'] = table_list[start+4].text.replace(" ", "")
            copy_of_fuel_data = {key: value[:] for key, value in fuel_data.items()}
            fuel_data_for_usa.append(copy_of_fuel_data)
        start+=5    
    return fuel_data_for_usa

def check_fuel_price(fuel_price):
    digit_count = 0
    for ch in fuel_price:
        if ch.isdigit():
            digit_count += 1
    return digit_count > 0
