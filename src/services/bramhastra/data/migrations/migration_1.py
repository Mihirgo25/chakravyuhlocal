from database.rails_db import get_connection
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder
from configs.fcl_freight_rate_constants import DEFAULT_SCHEDULE_TYPES, DEFAULT_PAYMENT_TERM,DEFAULT_RATE_TYPE
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.interaction.get_fcl_freight_local_rate_cards import get_fcl_freight_local_rate_cards
from micro_services.client import maps
import urllib
import json

BATCH_SIZE = 5000
REGION_MAPPING_URL = 'https://cogoport-production.sgp1.digitaloceanspaces.com/0860c1638d11c6127ab65ce104606100/id_region_id_mapping.json'

class PopulateFclFreightRateStatistics:
    def __init__(self) -> None:
        self.cogoback_connection = get_connection()
        
    def create_fcl_freight_rate_statistic_row(self, request):
        pass

    def get_like_dislike_count(self, rate_id, validity_id, feedback_type):
        query = FclFreightRateFeedback.select(FclFreightRateFeedback.id).where(FclFreightRateFeedback.fcl_freight_rate_id == rate_id and FclFreightRateFeedback.validity_id == validity_id and FclFreightRateFeedback.feedback_type == feedback_type)
        return query.count()
        pass
    
    def get_pricing_map_zone_ids(self,origin_port_id,destination_port_id) -> list:
        query  = FclFreightLocationCluster.select(FclFreightLocationClusterMapping.location_id,FclFreightLocationCluster.map_zone_id).join(FclFreightLocationClusterMapping).where(FclFreightLocationClusterMapping.location_id.in_([origin_port_id,destination_port_id]))
        map_zone_location_mapping = jsonable_encoder({item['location_id']: item['map_zone_id'] for item in query.dicts()})
        return map_zone_location_mapping.get(origin_port_id),map_zone_location_mapping.get(destination_port_id)
    
    def get_applicable_local_count(self, rate, key):
        trade_type = 'import' if key == 'destination' else 'export'
        
        request = {
            'trade_type':trade_type,
            'port_id':rate.get(f'{key}_port_id'),
            'country_id': rate.get(f'{key}_country_id'),
            'container_size': rate.get('container_size'),
            'container_type': rate.get('container_type'),
            'containers_count': rate.get('containers_count') or 0,
            'bls_count' : 1,
            'commodity' : rate.get('commodity'),
            'shipping_line_id' : rate.get('shipping_line_id')or None,
            'service_provider_id': rate.get('service_provider_id') or None,
            'rates': [],
            'cargo_weight_per_container': 18,
            'include_destination_dpd' : False,
            'additional_services':  [],
            'include_confirmed_inventory_rates':False,
            'return_count' : True,
        }
        
        response = get_fcl_freight_local_rate_cards(request)
        return response.get('count') or 0
        
    def populate_active_rate_ids(self):
        query = FclFreightRate.select().where(FclFreightRate.validities.is_null(False) and FclFreightRate.validities != '[]').order_by(FclFreightRate.id)
        total_count = query.count()
        
        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())
            print(type(REGION_MAPPING) ,'type')
        count = 0
        offset = 0
        row_data = []
        while offset < total_count:
            cur_query = query.offset(offset).limit(BATCH_SIZE)
            rates = jsonable_encoder(list(cur_query .dicts()))
            offset+= BATCH_SIZE
            for rate in rates: 
                for validity in rate['validities']:
                    count+= 1
                    identifier = '{}_{}_{}_{}'.format(rate['id'], validity['id'], validity.get('payment_term') or DEFAULT_PAYMENT_TERM , validity.get('schedule_type') or DEFAULT_SCHEDULE_TYPES)
                                
                    applicable_origin_local_count = self.get_applicable_local_count(rate, 'origin')
                    applicable_destination_local_count = self.get_applicable_local_count(rate,'destination')
                    row = {
                        'identifier' : identifier,
                        'validity_id' : validity.get('id'),
                        'rate_id' : rate.get('id'),
                        "commodity": rate.get('commodity'),
                        "container_size": rate.get('container_size'),
                        "container_type": rate.get('container_type'),
                        "containers_count": rate.get('containers_count') or 0,
                        "created_at": rate.get('created_at'),
                        "destination_country_id": rate.get('destination_country_id'),
                        "destination_local_id": rate.get('destination_local_id'),
                        "destination_detention_id": rate.get('destination_detention_id'),
                        "destination_main_port_id": rate.get('destination_main_port_id'),
                        "destination_port_id": rate.get('destination_port_id'),
                        "destination_trade_id": rate.get('destination_trade_id'),
                        "origin_country_id": rate.get('origin_country_id'),
                        "origin_local_id": rate.get('origin_local_id'),
                        "origin_detention_id": rate.get('origin_detention_id'),
                        "origin_demurrage_id": rate.get('origin_demurrage_id'),
                        "destination_demurrage_id": rate.get('destination_demurrage_id'),
                        "origin_main_port_id": rate.get('origin_main_port_id'),
                        "origin_port_id": rate.get('origin_port_id'),
                        "origin_trade_id": rate.get('origin_trade_id'),
                        "service_provider_id": rate.get('service_provider_id'),
                        "shipping_line_id": rate.get('shipping_line_id'),
                        "updated_at": rate.get('updated_at'),
                        "mode": rate.get('mode'),
                        "accuracy": rate.get('accuracy'),
                        "cogo_entity_id": rate.get('cogo_entity_id'),
                        "sourced_by_id": rate.get('sourced_by_id'),
                        "procured_by_id": rate.get('procured_by_id'),
                        "rate_type": rate.get('rate_type') or DEFAULT_RATE_TYPE,
                        "origin_region_id": REGION_MAPPING.get(rate.get('origin_port_id')),
                        "destination_region_id": REGION_MAPPING.get(rate.get('destination_port_id')),
                        "price": validity.get('price'),
                        "currency": validity.get('currency'),
                        "rate_created_at": rate.get('created_at'),
                        "rate_updated_at": rate.get('updated_at'),
                        "validity_created_at": rate.get('last_rate_available_date'),
                        "validity_updated_at": rate.get('last_rate_available_date'),
                        "payment_term": validity.get('payment_term'),
                        "schedule_type": validity.get('schedule_type'),
                        "market_price": validity.get('market_price') or validity.get('price'),
                        "validity_start": validity.get('validity_start'),
                        "validity_end": validity.get('validity_end'),
                        "applicable_origin_local_count": applicable_origin_local_count,
                        "applicable_destination_local_count": applicable_destination_local_count,
                    }
                    row_data.append(row)
                    print(count)
                if len(row_data) >= 100:
                    FclFreightRateStatistic.insert_many(row_data).execute()
                    row_data = []
                


def main():
    populate_from_rates = PopulateFclFreightRateStatistics()
    populate_from_rates.populate_active_rate_ids()

if __name__ == '__main__':   
    main()
