import pandas as pd, pickle, joblib, os
from configs.definitions import ROOT_DIR
from currency_converter import CurrencyConverter
from micro_services.client import common
from libs.get_distance import get_air_distance

def air_freight_preprocessing(air_freight_df):
    print('Data Preprocessing started....')
    air_freight_df['created_at'] =  pd.to_datetime(air_freight_df['created_at'], infer_datetime_format=True)

    #Changing price to USD
    air_freight_df['price_USD'] = air_freight_df.apply(lambda row: get_price_from_validities(row), axis=1, result_type='expand')

    air_freight_df['month_name'] = air_freight_df['created_at'].dt.strftime('%B')
    air_freight_df['day_name'] = air_freight_df['created_at'].dt.strftime('%A')

    #Alloting Ranks to Business Names according to Occurence and Price
    airline_ranks_path = os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models")
    airline_ranks = pickle.load(open(os.path.join(airline_ranks_path, "airline_ranks.pkl"), 'rb'))
    air_freight_df['airline_id'] = air_freight_df['airline_id'].astype(str)
    air_freight_df['airline_ranks'] = air_freight_df.airline_id.map(airline_ranks)

    #Calculating Distance w.r.t. Airport IDs    
    location_dict = joblib.load(open(os.path.join(ROOT_DIR, "services", "envision", "prediction_based_models", "air_location_dict.pkl") , "rb"))

    air_freight_df['air_distance']= air_freight_df.apply(lambda row: get_air_distance(
            location_dict.get(str(row['origin_airport_id']))[0], 
            location_dict.get(str(row['origin_airport_id']))[1], 
            location_dict.get(str(row['destination_airport_id']))[0], 
            location_dict.get(str(row['destination_airport_id']))[1]),
            axis=1)
    
    air_freight_df['volume'] = (air_freight_df['length']*air_freight_df['breadth']*air_freight_df['height'])/10**6
    air_freight_df.sort_values(by = 'created_at', ascending = True)
    air_freight_df.drop(['origin_airport_id','destination_airport_id','length','breadth', 'height', 'airline_id', 'created_at','weight_slabs'], axis = 1, inplace = True)
    air_freight_df.dropna(axis = 0, inplace = True)
    air_freight_df.drop_duplicates(inplace = True)
    air_freight_df.reset_index(drop = True, inplace = True)
    print('Data Preprocessing Done...')
    return air_freight_df

def get_price_from_validities(row):
    for slab in row.weight_slabs:
        if slab.get('lower_limit') >= 100 and slab.get('upper_limit') <= 300:
            price = slab.get('tariff_price')
            currency = slab.get('currency')

            if price:
                price_USD = currency_convertion(row, price, currency)        
                return price_USD
            break

def currency_convertion(row, price, currency):
    c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)
    try:
        return c.convert(price, currency, "USD", date = row.created_at)
    except:
        price = common.get_money_exchange_for_fcl(
                        {
                            "price": price,
                            "from_currency": currency,
                            "to_currency": "USD",
                        }
                )["price"]
    return price