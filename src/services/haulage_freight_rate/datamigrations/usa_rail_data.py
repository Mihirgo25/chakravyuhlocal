import requests
import json
import geopy.distance
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet

state_codes = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}


data1 = [
    ["01X", "Farm Products", "880", "992", "1105"],
    ["08X", "Forrest Products", "932", "1043", "1158"],
    ["11X", "Coal", "905", "1027", "1129"],
    ["14X", "Non-Metallic Minerals", "905", "1027", "1129"],
    ["20X", "Food and Kindered Products", "880", "992", "1105"],
    ["24X", "Lumber/Wood Products", "1079", "1191", "1304"],
    ["26X", "Pulp/Paper", "1135", "985", "1097"],
    ["28X", "Chemicals", "1517", "1573", "1629"],
    ["29X", "Petroleum Products", "1105", "1216", "1328"],
    ["32X", "Bricks/Concrete", "923", "1017", "1129"],
    ["33X", "Metal", "1067", "1180", "1292"],
    ["34X", "Fabricated Metal", "1044", "1172", "1287"],
    ["35X", "Machinery", "CMT", "CMT", "CMT"],
    ["36X", "Electrical Machinery", "CMT", "CMT", "CMT"],
    ["37X", "Transportation Equipment", "CMT", "CMT", "CMT"],
    ["40X", "Waste/Scrap", "880", "992", "1105"],
    ["41X", "Misc. Freight", "914", "1027", "1138"],
    ["42X", "Return Shipping Devices", "940", "985", "1165"],
    ["48X", "Hazardous Wastes", "4494", "4494", "4494"],
    ["49X", "Hazardous Material", "4494", "4494", "4494"]
]

data2 = [
    ["Farm Products", "845", "956", "1070"],
    ["Forrest Products", "898", "1009", "1120"],
    ["Coal", "871", "985", "1097"],
    ["Non-Metallic Minerals", "871", "985", "1097"],
    ["Food and Kindered Products", "845", "894", "1070"],
    ["Lumber/Wood Products", "1045", "1158", "1270"],
    ["Pulp/Paper", "955", "1067", "1180"],
    ["Chemicals", "1517", "1573", "1629"],
    ["Petroleum Products", "1120", "1181", "1293"],
    ["Bricks/Concrete", "886", "985", "1097"],
    ["Metal", "1067", "1180", "1292"],
    ["Fabricated Metal", "1027", "1138", "1251"],
    ["Machinery", "CMT", "CMT", "CMT"],
    ["Electrical Machinery", "CMT", "CMT", "CMT"],
    ["Transportation Equipment", "CMT", "CMT", "CMT"],
    ["Waste/Scrap", "845", "956", "1062"],
    ["Misc. Freight", "880", "986", "1105"],
    ["Return Shipping Devices", "905", "1017", "1129"],
    ["Hazardous Wastes", "4494", "4494", "4494"],
    ["Hazardous Material", "4494", "4494", "4494"]
]

GROUPING = [
    ['Austin, IN', '8562', '3'],
    ['Columbus, IN', '78485', '2'],
    ['Crothersville, IN', '8560', '2'],
    ['Edinburgh, IN', '8481', '1'],
    ['Franklin, IN', '78475', '1'],
    ['Greenwood, IN', '8471', '1'],
    ['Henryville, IN', '8570', '3'],
    ['Jeffersonville, IN', '78578', '3'],
    ['Louisville, KY', '78588', '3'],
    ['Scottsburg, IN', '8564', '3'],
    ['Seymour, IN', '8556', '2'],
    ['Sellersburg, IN', '8576', '3'],
    ['Southport, IN', '8469', '1'],
    ['Speed, IN', '8575', '3'],
    ['Taylorsville, IN', '8483', '2'],
    ['Whiteland, IN', '8473', '1']
            ]


def get_distance(origin,destination):

    coords_1 = origin
    coords_2 = destination
    return geopy.distance.geodesic(coords_1, coords_2).km

def make_groups(grouping):
    groups = {}
    for element in grouping:
        if element[-1] in groups:
            groups[element[-1]].append(element[0])
        else:
            groups[element[-1]] = []
            groups[element[-1]].append(element[0])

    return groups

group_number_pairs = make_groups(GROUPING)

def get_coordinates(group_number_pairs):
    group_place_coordinates = {}
    for group_number in group_number_pairs:
        for area in group_number_pairs[group_number]:
            area = area.split(',')
            q = area[0].strip() + '+' + state_codes[area[1].strip()]
            a = requests.get(f'https://nominatim.openstreetmap.org/search?format=geojson&q={q}')
            p = a.content 
            q = json.loads(p)
            if q['features']:
                latitude = q['features'][0]['geometry']['coordinates'][-1] 
                longitude = q['features'][0]['geometry']['coordinates'][0]
                if group_number in group_place_coordinates:
                    group_place_coordinates[group_number].append({area[0]:[latitude,longitude]})
                else:
                    group_place_coordinates[group_number] = []
                    group_place_coordinates[group_number].append({area[0]:[latitude,longitude]})

    return group_place_coordinates



def get_origin_coordinates(city,state_code):

    q = city.strip() + '+' + state_code.strip()
    a = requests.get(f'https://nominatim.openstreetmap.org/search?format=geojson&q={q}')
    p = a.content 
    q = json.loads(p)

    if q['features']:
        origin_latitude = q['features'][0]['geometry']['coordinates'][-1] 
        origin_longitude = q['features'][0]['geometry']['coordinates'][0]

    return [origin_latitude,origin_longitude]

def create_rail_haulage_rates(city,state_code):

    group_number_pairs = make_groups(GROUPING)
    group_place_coordinates = get_coordinates(group_number_pairs)
    origin = get_origin_coordinates(city,state_code)

    for element in group_place_coordinates:
        for places in group_place_coordinates[element]:
            for destination in places:
                coordinates = places[destination]
            total_distance = get_distance(origin,coordinates)
            for values in data2:
                if values[int(element)] == 'CMT':
                    continue
                query = {
                "distance" : total_distance,
                "commodity_class_type" : values[0],
                "base_price" : int(values[int(element)]),
                "train_load_type" : "Wagon Load",
                "currency" : "USD",
                "country_code" : "US",
                }

                query = HaulageFreightRateRuleSet.create(**query)

    return True

