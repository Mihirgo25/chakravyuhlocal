from database.rails_db import get_connection
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic
from services.bramhastra.models.checkout_air_freight_rate_statistic import CheckoutAirFreightRateStatistic
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE, DEFAULT_SCHEDULE_TYPES, DEFAULT_PAYMENT_TERM
from fastapi.encoders import jsonable_encoder
import urllib
import json
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

BATCH_SIZE = 1000
AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO = 166.67
REGION_MAPPING_URL = 'https://cogoport-production.sgp1.digitaloceanspaces.com/0860c1638d11c6127ab65ce104606100/id_region_id_mapping.json'
RATE_PARAMS = [ "commodity", "container_size","container_type", "destination_country_id", "destination_local_id", "destination_detention_id", "destination_main_port_id", "destination_port_id", "destination_trade_id", "origin_country_id", "origin_local_id", "origin_detention_id", "origin_demurrage_id", "destination_demurrage_id", "origin_main_port_id", "origin_port_id", "origin_trade_id", "service_provider_id", "shipping_line_id", "mode", "accuracy", "cogo_entity_id", "sourced_by_id", "procured_by_id"]
CANCELLATION_REASON_CHEAPER_RATE = [
    ['low','lower','cheap','cheaper','less','lesser','better', 'issue'],
    ['quot','price','amount','cost','offer']
]

CANCELLATION_REASON_LOW_RATE = [
    ['low','lower','less','lesser', 'issue'],
    ['rate','profit']
]
class MigrationHelpers:
    def get_chargeable_weight(volume, weight):
        volumetric_weight = volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
        if volumetric_weight > weight:
            chargeable_weight = volumetric_weight
        else:
            chargeable_weight = weight

        return chargeable_weight
    

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


class PopulateAirFreightRateStatistics(MigrationHelpers):
    def __init__(self) -> None:
        self.cogoback_connection = get_connection()
    
    def populate_active_rate_ids(self):
        query = AirFreightRate.select().where(AirFreightRate.validities.is_null(False) and AirFreightRate.validities != '[]').order_by(AirFreightRate.id)
        total_count = query.count()
        
        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())
        count = 0
        offset = 0
   
        while offset < total_count:
            cur_query = query.offset(offset).limit(BATCH_SIZE)
            rates = jsonable_encoder(list(cur_query .dicts()))
            offset+= BATCH_SIZE
            row_data = []
            for rate in rates: 
                for validity in rate['validities']:
                    count+= 1
                    
                    identifier = '{}_{}'.format(rate['id'], validity['id'])
                          
                    rate_params = {key: value for key, value in rate.items() if key in RATE_PARAMS} 
                    validity_params = self.get_validity_params(validity)
                    
                    row = {
                        **rate_params, 
                        **validity_params,
                        "containers_count": rate.get("containers_count") or 0,
                        'identifier' : identifier,
                        'rate_id' : rate.get('id'),
                        "rate_created_at": rate.get('created_at'),
                        "rate_updated_at": rate.get('updated_at'),
                        "rate_type": rate.get('rate_type') or DEFAULT_RATE_TYPE,
                        "origin_region_id": REGION_MAPPING.get(rate.get('origin_port_id')),
                        "destination_region_id": REGION_MAPPING.get(rate.get('destination_port_id')),
                        "market_price": validity.get('market_price') or validity.get('price'),
                        'validity_id' : validity.get('id'),
                    }
                    row_data.append(row)
                    print(count)
            AirFreightRateStatistic.insert_many(row_data).execute()

    def update_air_freight_rate_checkout_count(self):
        try:
            with self.cogoback_connection.cursor() as cur:

                sql = '''SELECT 
                        cs.id, cs.rate, cs.checkout_id, cs.created_at, cs.updated_at, cs.status,
                        co.shipment_id, co.source_id
                        FROM checkout_air_freight_services AS cs
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

                        statistics = AirFreightRateStatistic.select().where(
                            AirFreightRateStatistic.identifier == identifier,
                            AirFreightRateStatistic.sign == 1
                        ).first()
                        
                        if not statistics:
                            print("! Error: Identifier not present", identifier)
                        else:
                            setattr(statistics, 'checkout_count', statistics.checkout_count+1)
                            saved_status = statistics.save()
                            if not saved_status:
                                print("! Error: Couldn't save statistics", statistics.id)
                            else:
                                self.populate_checkout_air_freight_statistics(row,rate_card['rate_id'],rate_card['validity_id'])

                cur.close()
        except Exception as e:
            print('! Exception:',e)
    
    def populate_checkout_air_freight_statistics(self, checkout_stats, rate_id, validity_id):  
        try:
            params = {
                'checkout_air_freight_rate_services_id':checkout_stats[0],
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
                    self.populate_shipment_stats_in_air_freight_stats(rate_id, validity_id, params['shipment_id'])

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

                        cur.close()

                except Exception as e:
                    print('! Exception occured while fetching shipment_quotations:',e)

            CheckoutAirFreightRateStatistic.create(**params)
            print('Saved ...')

        except Exception as e:
            print('! Exception occured while populating checkout stats:',e)

    def populate_shipment_stats_in_air_freight_stats(self, rate_id, validity_id, shipment_id):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = f"""SELECT 
                        ss.state AS shipment_state, ss.cancellation_reason,
                        sf.state AS container_state, sf.packages_count
                        FROM shipments AS ss
                        LEFT JOIN shipment_air_freight_services AS sf 
                        ON ss.id = sf.shipment_id
                        WHERE ss.id = '{shipment_id}'
                    """
                cur.execute(sql)
                result = cur.fetchone()
                shipment_state = result[0]
                cancellation_reason = result[1]
                container_state = result[2]
                packages_count = result[3]

                identifier = rate_id + '_' + validity_id
                statistic = AirFreightRateStatistic.select().where(
                    AirFreightRateStatistic.identifier == identifier,
                    AirFreightRateStatistic.sign == 1
                ).first()
                
                setattr(statistic, 'packages_count', statistic.packages_count+packages_count)
                
                if(shipment_state=='completed'):
                    setattr(statistic, 'shipment_completed_count', statistic.shipment_completed_count+1)
                elif(shipment_state=='aborted'):
                    setattr(statistic, 'shipment_aborted_count', statistic.shipment_aborted_count+1)  
                elif(shipment_state=='in_progress'):
                    setattr(statistic, 'shipment_is_active_count', statistic.shipment_is_active_count+1)  
                elif(shipment_state=='shipment_received'):
                    setattr(statistic, 'shipment_received_count', statistic.shipment_received_count+1)
                elif(shipment_state=='confirmed_by_importer_exporter'):
                    setattr(statistic, 'shipment_confirmed_by_importer_exporter_count', statistic.shipment_confirmed_by_importer_exporter_count+1)
                elif(shipment_state=='cancelled'):
                    setattr(statistic, 'shipment_cancelled_count', statistic.shipment_cancelled_count+1) 

                if(container_state=='confirmed_by_service_provider'):
                    setattr(statistic, 'shipment_confirmed_by_service_provider_count', statistic.shipment_confirmed_by_service_provider_count+1)
                elif(container_state=='awaiting_service_provider_confirmation'):
                    setattr(statistic, 'shipment_awaited_service_provider_confirmation_count', statistic.shipment_awaited_service_provider_confirmation_count+1)
                elif(container_state=='init'):
                    setattr(statistic, 'shipment_init_count', statistic.shipment_init_count+1)
                elif(container_state=='flight_arrived'):
                    setattr(statistic, 'shipment_flight_arrived_count', statistic.shipment_flight_arrived_count+1)
                elif(container_state=='flight_departed'):
                    setattr(statistic, 'shipment_flight_departed_count', statistic.shipment_flight_departed_count+1)
                elif(container_state=='cargo_handed_over_at_origin'):
                    setattr(statistic, 'shipment_cargo_handed_over_at_origin_count', statistic.shipment_cargo_handed_over_at_origin_count+1)
                elif(container_state=='cargo_handed_over_at_destination'):
                    setattr(statistic, 'shipment_cargo_handed_over_at_destination_count', statistic.shipment_cargo_handed_over_at_destination_count+1)

                saved_status = statistic.save()
                if not saved_status:
                    print("! Error: Couldn't save statistics", statistic.id)
                else:
                    print('Saved ...',statistic.id)

                cur.close()

        except Exception as e:
            print('! Exception occured while populating shipment stats:',e)



            
def main():
    # populate_from_rates = PopulateFclFreightRateStatistics()
    pass

if __name__ == '__main__':   
    main()