from services.air_freight_rate.constants.air_freight_rate_constants import (
    AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO,
    AIR_IMPORTS_LOW_DENSITY_RATIO,
    AIR_IMPORTS_HIGH_DENSITY_RATIO,
    AIR_EXPORTS_LOW_DENSITY_RATIO,
    AIR_EXPORTS_HIGH_DENSITY_RATIO,
    PROCURE_NON_AVAILABLE_RATE_FROM_CARGOAI
)
from micro_services.client import spot_search,maps,common
from datetime import datetime, timedelta
from configs.global_constants import SERVICE_PROVIDER_FF,MAX_VALUE
from services.air_freight_rate.interactions.get_weight_slabs_for_airline import get_weight_slabs_for_airline
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate
from services.air_freight_rate.interactions.create_air_freight_rate_surcharge import create_air_freight_rate_surcharge
from database.rails_db import get_operators

def get_density_wise_rate_card(
    response_object, trade_type, gross_weight, gross_volume, chargeable_weight
):
    ratio = round(
        (
            (gross_volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO)
            / float(gross_weight)
        ),
        4,
    )
    density_rate_present = False
    density_rate_category = "general"
    density_weight = round(float(gross_weight) / (gross_volume), 2)
    if trade_type == "import":
        low_density_lower_limit = AIR_IMPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_IMPORTS_HIGH_DENSITY_RATIO
    else:
        low_density_lower_limit = AIR_EXPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_EXPORTS_HIGH_DENSITY_RATIO

    freights = []
    if ratio > low_density_lower_limit:
        closest_density_match = {}
        minimum_possible = MAX_VALUE
        density_rate_category = "low_density"
        for freight in response_object["freights"]:
            density_difference = abs(
                int(freight["min_density_weight"]) - int(density_weight)
            )
            if (
                int(freight["min_density_weight"]) == int(density_weight)
                and freight["density_category"] == "low_density"
            ):
                density_rate_present = True
                freights.append(freight)
            elif (
                density_difference < minimum_possible
                and freight["density_category"] == "low_density"
            ):
                minimum_possible = density_difference
                closest_density_match = freight
        if closest_density_match:
            freights.append(closest_density_match)
    elif ratio <= high_density_upper_limit and chargeable_weight >= 100:
        density_rate_category = "high_density"
        for freight in response_object["freights"]:
            if (
                freight["min_density_weight"] <= density_weight
                and freight["max_density_weight"] > density_weight
                and freight["density_category"] == "high_density"
            ):
                density_rate_present = True
                freights.append(freight)
            elif freight["density_category"] == "general":
                freights.append(freight)
    else:
        for freight in response_object["freights"]:
            if freight["density_category"] == "general":
                freights.append(freight)

        # If no rate available show low in general as price is going to be always higher
        if len(freights) == 0:
            for freight in response_object["freights"]:
                if freight["density_category"] == "low_density":
                    freights.append(freight)
        
    if density_rate_category == "high_density" and density_rate_present:
        freights = [
            freight_object
            for freight_object in freights
            if freight_object["density_category"] != "general"
        ]

    if not freights:
        return {}

    response_object["freights"] = freights

    return response_object

def get_rate_from_cargo_ai(air_freight_rate, feedback, performed_by_id):
    params_for_cargoai = {}
    spot_search_detail=spot_search.get_spot_search({"id": str(feedback.source_id)})['detail']

    if not spot_search_detail:
        return 
    cargo_clearance_date = spot_search_detail['cargo_clearance_date']
    cargo_clearance_date = datetime.strptime(cargo_clearance_date, '%Y-%m-%d').date()
    cargo_clearance_date = cargo_clearance_date + timedelta(days=1)
    params_for_cargoai['departure_date']=cargo_clearance_date
    params_for_cargoai['origin_airport_id'] = spot_search_detail['origin_airport_id']
    params_for_cargoai['destination_airport_id'] = spot_search_detail['destination_airport_id']

    airport_locs=maps.list_locations({"filters":{"id":[params_for_cargoai['origin_airport_id'],params_for_cargoai['destination_airport_id']],"type":"airport","status":"active"}})['list']

    if airport_locs[0]['id'] == params_for_cargoai['origin_airport_id']:
        origin =  airport_locs[0]['port_code']
        destination = airport_locs[1]['port_code']
    else:
        origin = airport_locs[1]['port_code']
        destination = airport_locs[0]['port_code']

    params_for_cargoai['origin'] = origin
    params_for_cargoai['destination']=destination
    params_for_cargoai['commodity'] = spot_search_detail['commodity']
    params_for_cargoai['volume'] = spot_search_detail['volume']
    params_for_cargoai['packages_count'] = spot_search_detail.get('package_count', 1)
    params_for_cargoai['weight'] = spot_search_detail['weight']
    params_for_cargoai['commodity_details'] = spot_search_detail['commodity_details']
    params_for_cargoai['time'] = 25

    try:
        all_rates = common.get_air_routes_and_schedules_from_cargo_ai(params_for_cargoai)
    except Exception as e:
        raise
    if not all_rates:
        return 
    rates_for_airlines = make_entry_in_rates(all_rates, params_for_cargoai)
    if rates_for_airlines:
        importer_exporter_id=spot_search_detail['importer_exporter_id']
        variables = { 'origin': airport_locs[params_for_cargoai['origin_airport_id']], 'destination': airport_locs[params_for_cargoai['destination_airport_id']], 'spot_search_id': feedback.source_id, importer_exporter_id: importer_exporter_id, 'airlines': rates_for_airlines }
        notification_to_sales_agent_for_rate_added(air_freight_rate, performed_by_id, variables)

def make_entry_in_rates(all_rates, params_for_cargoai):
     rates_for_airlines = []
     if all_rates and all_rates.get('flights'):
        chargeable_weight = get_chargeable_weight(params_for_cargoai['weight'], params_for_cargoai['volume'])
        density_params = get_density_ratio_and_category(params_for_cargoai['weight'], params_for_cargoai['volume'], params_for_cargoai['trade_type'])
        density_ratio = density_params['density_ratio']
        density_category = density_params['density_category']
        operation_types = ['passenger', 'freighter']

        for individual_rate in all_rates['flights']:
            if individual_rate['available'] or PROCURE_NON_AVAILABLE_RATE_FROM_CARGOAI:
                if individual_rate['airlineCode'] == '00': 
                    individual_rate['airlineCode'] = 'OO' 
                airline_details = get_operators(iata_code=individual_rate['airlineCode'],operator_type='airline')
                if not airline_details :
                    continue
                airline_details = airline_details[0]
                final_weight_slabs = get_weight_slabs_for_airline(airline_id=airline_details['id'],chargeable_weight=chargeable_weight,overweight_upper_limit=100.0)
                if not final_weight_slabs:
                    continue
                final_weight_slab = final_weight_slabs[0]
                rates_for_airlines.append(airline_details['business_name'])

                for rate in individual_rate['rates']:
                    if rate.get('allInRate') and  params_for_cargoai.get('commodity_details'):
                        for operation_type in operation_types:
                            cargo_param = { 'airline_id': airline_details[:id], 'operation_type': operation_type, 'flight_uuid': individual_rate['flightUID'], 'density_category': density_category, 'density_ratio': density_ratio, 'service_provider_ff': SERVICE_PROVIDER_FF, 'price_type': 'all_in', 'final_weight_slab': final_weight_slab }
                            new_params = params_for_cargoai | cargo_param
                            create_params = get_create_params(new_params, rate, SERVICE_PROVIDER_FF)
                            create_air_freight_rate(create_params)
                    
                    if rate.get('netRate') and rate.get('allInRate') != rate.get('netRate') and params_for_cargoai.get('commodity_details'):
                        for operation_type in operation_types:
                            cargo_param = { 'airline_id': airline_details[:id], 'operation_type': operation_type, 'flight_uuid': individual_rate['flightUID'], 'density_category': density_category, 'density_ratio': density_ratio, 'service_provider_ff': SERVICE_PROVIDER_FF, 'price_type': 'net_net', 'final_weight_slab': final_weight_slab }
                            new_params = params_for_cargoai | cargo_param
                            create_params = get_create_params(new_params, rate, SERVICE_PROVIDER_FF)
                            create_air_freight_rate(create_params)
                    if rate.get('netRate') and rate.get('charges') and params_for_cargoai.get('commodity_details') and rate['netRate'] != 0:
                        line_items = []
                        for item in rate['charges']:
                            line_item = {}
                            if item['code'] == 'MY':
                                item['code'] = 'FSC'
                            line_item['code'] = item['code'].upper()
                            line_item['unit'] = 'per_kg'
                            line_item['price'] = item['rate']
                            line_item['min_price'] = item['minAmount']
                            line_item['currency'] = rate['currency']
                            line_items.append(line_item)
                        for operation_type in operation_types:
                            create_air_freight_rate_surcharge({'origin_airport_id': params_for_cargoai['origin_airport_id'], 'destination_airport_id': params_for_cargoai['destination_airport_id'], 'commodity': params_for_cargoai['commodity'], 'commodity_type': params_for_cargoai['commodity_details'][0]['commodity_type'], 'airline_id': airline_details['id'], 'operation_type': operation_type, 'currency': rate['currency'], 'price_type': 'net_net', 'service_provider_id': SERVICE_PROVIDER_FF, 'performed_by_id': SERVICE_PROVIDER_FF, 'procured_by_id': SERVICE_PROVIDER_FF, 'sourced_by_id': SERVICE_PROVIDER_FF, 'line_items': line_items})

     return rates_for_airlines
                

def get_create_params(params,rate,service_provider_id):
    beginning_of_the_day =datetime.now().date()
    weight_slabs = [{**params.get('final_weight_slabs'),'tariff_price':rate['allInRate'],'currency':rate['currency']}] 
    return { 'origin_airport_id': params['origin_airport_id'], 'destination_airport_id': params['destination_airport_id'], 'commodity': params['commodity'], 'commodity_type': params['commodity_details'][0]['commodity_type'], 'commodity_sub_type': params['commodity_details'][0]['commodity_subtype'], 'airline_id': params['airline_id'], 'operation_type': params['operation_type'], 'currency': rate['currency'], 'price_type': params['price_type'], 'service_provider_id': service_provider_id, 'performed_by_id': service_provider_id, 'procured_by_id': service_provider_id, 'sourced_by_id': service_provider_id, 'shipment_type': 'box', 'stacking_type': 'stackable', 'weight_slabs': weight_slabs, 'validity_start': beginning_of_the_day, 'validity_end': params['departure_date'], 'external_rate_id': rate[:id], 'flight_uuid': params['flight_uuid'], 'density_category': params['density_category'], 'density_ratio': params['density_ratio'], 'source': 'cargo_ai' }

def get_chargeable_weight(weight, volume):
    volumetric_weight = volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    chargeable_weight = volumetric_weight if volumetric_weight > weight else weight
    return round(chargeable_weight,2)

def get_density_ratio_and_category(weight, volume, trade_type):
    ratio = (volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO / weight)
    ratio = round(ratio, 4)
    density_category = 'general'
    density_ratio = '1:1'
    density_weight = (weight / volume)
    if trade_type == 'import':
        low_density_lower_limit =AIR_IMPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_IMPORTS_HIGH_DENSITY_RATIO
    else:
        low_density_lower_limit =AIR_EXPORTS_LOW_DENSITY_RATIO
        high_density_upper_limit = AIR_EXPORTS_HIGH_DENSITY_RATIO

    chargeable_weight = get_chargeable_weight(weight, volume)
    if ratio > low_density_lower_limit:
      density_category = 'low_density'
      density_ratio = f'1:{density_weight}'
    elif ratio <= high_density_upper_limit and  chargeable_weight >= 100:
      density_category = 'high_density'
      if density_weight >= 500:
        density_ratio = '1:500'
      elif density_weight >= 300:
        density_ratio = '1:300'
      elif density_weight >= 250:
        density_ratio = '1:250'
      else:
        density_ratio = '1:200'

    return { 'density_category': density_category, 'density_ratio': density_ratio }


def notification_to_sales_agent_for_rate_added(air_freight_rate, performed_by_id, variables):
    data={
        'user_id': performed_by_id,
        'type': 'platform_notification',
        'service': 'air_freight_rate',
        'service_id': air_freight_rate['id'],
        'template_name': 'cargoai_notification_to_sales_agent',
        'variables': variables
    }
    common.create_communication(data)