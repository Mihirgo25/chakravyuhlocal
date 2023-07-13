from database.rails_db import get_connection
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.shortcuts import model_to_dict

class PopulateFclFreightRateStatistics:
    def __init__(self) -> None:
        self.cogoback_connection = get_connection()

def populate_from_rates():
    
    
def run():
    for fcl_freight_rate in FclFreightRate.select():
        for validity in fcl_freight_rate.validities:    
            row = {
                'rate_id': fcl_freight_rate.id,
                'unique_id': ''.join([str(fcl_freight_rate.id),validity['id']]).replace("-", ""),
                'origin_port_id': fcl_freight_rate.origin_port_id,
                'destination_port_id': fcl_freight_rate.destination_port_id,
                'origin_main_port_id': fcl_freight_rate.origin_main_port_id,
                'destination_main_port_id':  fcl_freight_rate.destination_main_port_id,
                'origin_country_id': fcl_freight_rate.origin_country_id,
                'destination_country_id': fcl_freight_rate.destination_country_id,
                'origin_continent_id': fcl_freight_rate.origin_continent_id,
                'destination_continent_id': fcl_freight_rate.destination_continent_id,
                'origin_trade_id': fcl_freight_rate.origin_trade_id,
                'destination_trade_id': fcl_freight_rate.destination_rate_id,
                'origin_pricing_zone_map_id': None,
                'destination_pricing_zone_map_id': None,
                'shipping_line_id': fcl_freight_rate.shipping_line_id,
                'currency': validity['currency'],
                'accuracy': None,
                'mode': fcl_freight_rate.id
        
            }
    




def main():
    populate_from_rates = PopulateFclFreightRateStatistics()
    populate_from_rates.run()

if __name__ == '__main__':   
    main()
