from database.rails_db import get_connection
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder
from configs.fcl_freight_rate_constants import DEFAULT_SCHEDULE_TYPES, DEFAULT_PAYMENT_TERM,DEFAULT_RATE_TYPE
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import CheckoutFclFreightRateStatistic
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.interaction.get_fcl_freight_local_rate_cards import get_fcl_freight_local_rate_cards
from micro_services.client import maps
import urllib
import json
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

BATCH_SIZE = 5000
REGION_MAPPING_URL = 'https://cogoport-production.sgp1.digitaloceanspaces.com/0860c1638d11c6127ab65ce104606100/id_region_id_mapping.json'

CANCELLATION_REASON_CHEAPER_RATE = [
    ['low','lower','cheap','cheaper','less','lesser','better', 'issue'],
    ['quot','price','amount','cost','offer']
]

CANCELLATION_REASON_LOW_RATE = [
    ['low','lower','less','lesser', 'issue'],
    ['rate','profit']
]
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

    def stem_words_using_nltk(self, sentence):
        words = word_tokenize(sentence)
        stemmer = PorterStemmer()
        stemmed_words = [stemmer.stem(word) for word in words]
        return stemmed_words
    
    def cancellation_reason_matching(self, stemmed_words, arr):
        flag = 0
        for word in arr[0]:
            if(word in stemmed_words):
                flag = 1
        if(flag == 1):
            for word in arr[1]:
                if(word in stemmed_words):
                    flag += 1
        if(flag > 1):
            return True
        return False


    def populate_shipment_stats_in_fcl_freight_stats(self, rate_id, validity_id, shipment_id):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = f"""SELECT 
                        ss.state AS shipment_state, ss.cancellation_reason,
                        sf.state AS container_state, sf.containers_count
                        FROM shipments AS ss
                        LEFT JOIN shipment_fcl_freight_services AS sf 
                        ON ss.id = sf.shipment_id
                        WHERE ss.id = '{shipment_id}'
                    """
                cur.execute(sql)
                result = cur.fetchone()
                shipment_state = result[0]
                cancellation_reason = result[1]
                container_state = result[2]
                containers_count = result[3]

                identifier = rate_id + '_' + validity_id
                statistic = FclFreightRateStatistic.select().where(
                            FclFreightRateStatistic.identifier == identifier,
                            FclFreightRateStatistic.sign == 1
                        ).first()
                
                setattr(statistic, 'containers_count', statistic.containers_count+containers_count)
                
                if(shipment_state=='completed'):
                    setattr(statistic, 'shipment_completed_count', statistic.shipment_completed_count+1)
                elif(shipment_state=='aborted'):
                    setattr(statistic, 'shipment_aborted_count', statistic.shipment_aborted_count+1)  
                elif(shipment_state=='in_progress'):
                    setattr(statistic, 'shipment_is_active_count', statistic.shipment_is_active_count+1)  
                elif(shipment_state=='shipment_received'):
                    setattr(statistic, 'shipment_awaited_service_provider_confirmation_count', statistic.shipment_awaited_service_provider_confirmation_count+1)
                elif(shipment_state=='confirmed_by_importer_exporter'):
                    setattr(statistic, 'shipment_confirmed_by_service_provider_countb', statistic.shipment_confirmed_by_service_provider_countb+1)
                elif(shipment_state=='cancelled'):
                    setattr(statistic, 'shipment_cancelled_count', statistic.shipment_cancelled_count+1) 
                    
                    stem_words = self.stem_words_using_nltk(cancellation_reason)
                    if self.cancellation_reason_matching(stem_words, CANCELLATION_REASON_CHEAPER_RATE):
                        setattr(
                            statistic, 
                            'shipment_cancellation_reason_got_a_cheaper_rate_from_my_service_provider_count', 
                            statistic.shipment_cancellation_reason_got_a_cheaper_rate_from_my_service_provider_count+1
                        )
                    elif self.cancellation_reason_matching(stem_words, CANCELLATION_REASON_LOW_RATE):
                        setattr(
                            statistic, 
                            'shipment_booking_rate_is_too_low_count', 
                            statistic.shipment_booking_rate_is_too_low_count+1
                        )

                if(container_state=='containers_gated_out'):
                    setattr(statistic, 'shipment_containers_gated_out_count', statistic.shipment_containers_gated_out_count+1)
                elif(container_state=='containers_gated_in'):
                    setattr(statistic, 'shipment_containers_gated_in_count', statistic.shipment_containers_gated_in_count+1)
                elif(container_state=='init'):
                    setattr(statistic, 'shipment_init_count', statistic.shipment_init_count+1)
                elif(container_state=='vessel_arrived'):
                    setattr(statistic, 'shipment_vessel_arrived_count', statistic.shipment_vessel_arrived_count+1)

                saved_status = statistic.save()
                if not saved_status:
                    print("! Error: Couldn't save statistics", statistic.id)
                else:
                    print('Saved ...',statistic.id)

        except Exception as e:
            print('! Exception occured while populating shipment stats:',e)

    def populate_checkout_fcl_freight_statistics(self, checkout_stats, rate_id, validity_id):  
        try:
            params = {
                'checkout_fcl_freight_rate_services_id':checkout_stats[0],
                'checkout_id':checkout_stats[2],
                'created_at':checkout_stats[3],
                'updated_at':checkout_stats[4],
                'status':checkout_stats[5],
                'shipment_id':checkout_stats[6],
                'spot_search_id':checkout_stats[7],
                'rate_id':rate_id,
                'validity_id':validity_id,
            }

            if(params['shipment_id']):
                try:
                    self.populate_shipment_stats_in_fcl_freight_stats(rate_id, validity_id, params['shipment_id'])

                    with self.cogoback_connection.cursor() as cur:
                        sql = f"SELECT id FROM shipment_buy_quotations where shipment_id = '{params['shipment_id']}'"
                        cur.execute(sql)
                        result = cur.fetchall()
                        if(result):
                            params['buy_quotation_id'] = result[0][0]

                        sql = f"SELECT id FROM shipment_sell_quotations where shipment_id = '{params['shipment_id']}'"
                        cur.execute(sql)
                        result = cur.fetchall()
                        if(result):
                            params['sell_quotation_id'] = result[0][0]


                except Exception as e:
                    print('! Exception occured while fetching shipment_quotations:',e)

            CheckoutFclFreightRateStatistic.create(**params)
            print('Saved ...')

        except Exception as e:
            print('! Exception occured while populating checkout stats:',e)


    def update_fcl_freight_rate_checkout_count(self):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = '''SELECT 
                        cs.id, cs.rate, cs.checkout_id, cs.created_at, cs.updated_at, cs.status,
                        co.shipment_id, co.source_id
                        FROM checkout_fcl_freight_services AS cs
                        LEFT JOIN checkouts AS co 
                        ON cs.checkout_id = co.id
                        WHERE cs.rate ? 'rate_id'
                    '''
                cur.execute(sql)

                for row in cur:
                    rate_card = row[1]
                    if(
                        'rate_id' in rate_card and 'validity_id' in rate_card and 
                        rate_card['rate_id'] and rate_card['validity_id']
                    ):
                        identifier = rate_card['rate_id']+'_'+rate_card['validity_id']

                        statistics = FclFreightRateStatistic.select().where(
                                FclFreightRateStatistic.identifier == identifier,
                                FclFreightRateStatistic.sign == 1
                            ).first()
                        
                        if not statistics:
                            print("! Error: Identifier not present", identifier)
                        else:
                            setattr(statistics, 'checkout_count', statistics.checkout_count+1)
                            saved_status = statistics.save()
                            if not saved_status:
                                print("! Error: Couldn't save statistics", statistics.id)
                            else:
                                self.populate_checkout_fcl_freight_statistics(row,rate_card['rate_id'],rate_card['validity_id'])

        except Exception as e:
            print('! Exception:',e)

def main():
    populate_from_rates = PopulateFclFreightRateStatistics()
    # populate_from_rates.populate_active_rate_ids()
    populate_from_rates.update_fcl_freight_rate_checkout_count()
    # populate_from_rates.populate_shipment_stats_in_fcl_freight_stats('3041971d-e71d-4556-b580-a986c429d173','727919d1-a079-4b87-85d2-3227a6c392b2','18cff673-651a-41cd-869a-b560ba246dda')

if __name__ == '__main__':   
    main()
