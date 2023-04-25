from configs.rate_averages import AVERAGE_RATES
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from configs.trade_lane import TRADE_LANE_PRICES
import concurrent.futures

def migration_of_countries():
    final=[]
    print(len(AVERAGE_RATES)+len(TRADE_LANE_PRICES))
    for key,value in AVERAGE_RATES.items():
        if key=='default':
            continue
        row={}
        locations_size = key.split(':')
        row['origin_location_id']=locations_size[0]
        row['destination_location_id'] = locations_size[1]
        row['container_size'] = locations_size[2]
        row['origin_location_type'] = 'country'
        row['destination_location_type']='country'
        row['container_type'] = 'standard'
        row['commodity'] = 'general'
        row['line_items'] = {'code':'BAS','unit':'per_container','lower_price':value,'upper_price':value,'remarks':[],'currency':'USD'}
        final.append(row)
    
    for key,value in TRADE_LANE_PRICES.items():
        if key=='default':
            continue
        row={}
        locations_size = key.split(':')
        row['origin_location_id']=locations_size[0]
        row['destination_location_id'] = locations_size[1]
        row['container_size'] = locations_size[2]
        row['origin_location_type'] = 'trade'
        row['destination_location_type']='trade'
        row['container_type'] = 'general'
        row['commodity'] = 'standard'
        row['line_items'] = {'code':'BAS','unit':'per_container','lower_price':value,'upper_price':value,'remarks':[],'currency':'USD'}
        final.append(row)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        futures = [executor.submit(insert_into_table, row) for row in final]



def insert_into_table(row):
    fcl_estimation = FclFreightRateEstimation(**row)
    fcl_estimation.save()


    


