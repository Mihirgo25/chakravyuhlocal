import requests
from bs4 import BeautifulSoup
from micro_services.client import maps

# Send a GET request to the website
def find_electricity_price():
    url = 'https://www.globalpetrolprices.com/india/electricity_prices/'
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    data = []
    div_element_price = soup.find('div', {'id': 'graphic'})
    div_element_country = soup.find('div', {'id': 'outsideLinks'})
    div_data = div_element_price.text
    div_data_country = div_element_country.text
    country = div_data.splitlines()
    filtered_country = [element for element in country if element]
    for country in filtered_country:
        input = {"filters": {"q": country, 'type': 'country'}}
        locations_data_ = maps.list_locations(input)["list"][0]['country_code']

    price = div_data_country.splitlines()
    filtered_price = [element for element in price if element]
    price_country_mapping = {}
    for i in range(len(filtered_price)):
        price_country_mapping[filtered_country[i]] = filtered_price[i]
    return price_country_mapping