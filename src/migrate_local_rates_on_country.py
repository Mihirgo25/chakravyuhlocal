from configs.definitions import ROOT_DIR
import pandas as pd, os, copy
from services.fcl_freight_rate.interaction.add_local_rates_on_country import add_local_rates_on_country

def migrate_local_rates_on_country():
    """
    Name of the migration file - estimated_local_rates.csv
    """
    FILE_PATH = os.path.join(ROOT_DIR, "local_rates_on_country.csv")
    estimated_rates = pd.read_csv(FILE_PATH)
    final_create_params = get_country_wise_locals_from_sheet(estimated_rates)
    response = create_fcl_locals(final_create_params)
    return response

def get_country_wise_locals_from_sheet(estimated_rates):
    dict_list = []
    row_dict = {}
    for _, row in estimated_rates.iterrows():
        row_dict = {col: row[col] for col in estimated_rates.columns}
        line_items = set_local_line_items(row_dict['line_items'])
        row_dict['container_size'] = str(row_dict['container_size'])
        row_dict['data'] = {'plugin':None, 'detention':None, 'demurrage':None, 'line_items':line_items}
        dict_list.append(row_dict)

    return dict_list

def create_fcl_locals(local_rate_params):
    for param in local_rate_params:
        add_local_rates_on_country(param)
    # with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
    #     futures = [executor.submit(add_local_rates_on_country, query) for query in local_rate_params]
    return {"message":"Creating rates"}

def set_local_line_items(local_rate):
    line_items = []
    rate = copy.deepcopy(eval(local_rate))
    for line_item in rate:
        local_price = round((line_item['upper_price'] + line_item['lower_price'])/2)
        if local_price > 0 and (local_price%10 != 0):
            line_item['price'] = local_price + (5 - local_price%10) if local_price%10 <= 5 else (local_price + (10 - local_price%10))
        else:
            line_item['price'] = local_price
        del line_item['upper_price']
        del line_item['lower_price']
        line_items.append(line_item)
    return line_items