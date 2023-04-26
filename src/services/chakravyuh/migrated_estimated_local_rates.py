from configs.definitions import ROOT_DIR
import pandas as pd, concurrent.futures, os 
from services.chakravyuh.models.fcl_freight_rate_local_estimation import FclFreightRateLocalEstimation
### change file path######

def migrate_estimated_local_rates():
    """
    Name of the migration file - estimated_local_rates.csv
    """

    FILE_PATH = os.path.join(ROOT_DIR, "services", "chakravyuh", "estimated_local_rates.csv")
    estimated_rates = pd.read_csv(FILE_PATH)
    final_create_params = []

    search_wise_params = ['country', 'trade', 'continent']
    for param in search_wise_params:
        dict_list = eval('add_'+param+'(estimated_rates)')
        final_create_params.extend(dict_list)
    with concurrent.futures.ThreadPoolExecutor(max_workers = len(final_create_params)) as executor:
        futures = [executor.submit(insert_into_table, row) for row in final_create_params]

def add_continent(estimated_rates):
    selected_cols = ['Continent','trade_type','shipping_line','container_type','container_size','commodity','line_items','local_currency']
    dict_list = []
    row_dict = {}
    for _, row in estimated_rates[selected_cols].iterrows():
        row_dict = {col: row[col] for col in selected_cols}
        row_dict['location_id'] = row['Continent']
        del row_dict['Continent']
        row_dict['location_type'] = 'continent'
        row_dict['line_items'] = eval(row_dict['line_items'])
        dict_list.append(row_dict)
    
    return dict_list


def add_country(estimated_rates):
    selected_cols = ['Country','trade_type','shipping_line','container_type','container_size','commodity','line_items','local_currency']
    dict_list = []
    row_dict = {}
    for _, row in estimated_rates[selected_cols].iterrows():
        row_dict = {col: row[col] for col in selected_cols}
        row_dict['location_id'] = row['Country']
        row_dict['location_type'] = 'country'
        row_dict['line_items'] = eval(row_dict['line_items'])
        del row_dict['Country']
        dict_list.append(row_dict)

    return dict_list


def add_trade(estimated_rates):
    selected_cols = ['Trade','trade_type','shipping_line','container_type','container_size','commodity','line_items','local_currency']
    dict_list = []
    row_dict = {}
    for _, row in estimated_rates[selected_cols].iterrows():
        row_dict = {col: row[col] for col in selected_cols}
        row_dict['location_id'] = row['Trade']
        row_dict['location_type'] = 'trade'
        row_dict['line_items'] = eval(row_dict['line_items'])
        del row_dict['Trade']
        dict_list.append(row_dict)
    
    return dict_list

def insert_into_table(row):
    fcl_local_estimation = FclFreightRateLocalEstimation(**row)
    fcl_local_estimation.save()