from database.rails_db import get_connection
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE, DEFAULT_SCHEDULE_TYPES, DEFAULT_PAYMENT_TERM
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import FeedbackFclFreightRateStatistic
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import CheckoutFclFreightRateStatistic
from services.bramhastra.models.fcl_freight_rate_request_statistics import FclFreightRateRequestStatistic
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.fcl_freight_rate.interaction.get_fcl_freight_local_rate_cards import get_fcl_freight_local_rate_cards
from database.rails_db import get_connection
from playhouse.shortcuts import model_to_dict
from micro_services.client import common
import urllib
import json
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

BATCH_SIZE = 1000
REGION_MAPPING_URL = 'https://cogoport-production.sgp1.digitaloceanspaces.com/0860c1638d11c6127ab65ce104606100/id_region_id_mapping.json'
CANCELLATION_REASON_CHEAPER_RATE = [
    ['low','lower','cheap','cheaper','less','lesser','better', 'issue'],
    ['quot','price','amount','cost','offer']
]

CANCELLATION_REASON_LOW_RATE = [
    ['low','lower','less','lesser', 'issue'],
    ['rate','profit']
]
RATE_PARAMS = [ "commodity", "container_size","container_type", "destination_country_id", "destination_local_id", "destination_detention_id", "destination_main_port_id", "destination_port_id", "destination_trade_id", "origin_country_id", "origin_local_id", "origin_detention_id", "origin_demurrage_id", "destination_demurrage_id", "origin_main_port_id", "origin_port_id", "origin_trade_id", "service_provider_id", "shipping_line_id", "mode", "accuracy", "cogo_entity_id", "sourced_by_id", "procured_by_id"]

class MigrationHelpers:
    def get_pricing_map_zone_ids(self,origin_port_id,destination_port_id) -> list:
        query  = FclFreightLocationCluster.select(FclFreightLocationClusterMapping.location_id,FclFreightLocationCluster.map_zone_id).join(FclFreightLocationClusterMapping).where(FclFreightLocationClusterMapping.location_id.in_([origin_port_id,destination_port_id]))
        map_zone_location_mapping = jsonable_encoder({item['location_id']: item['map_zone_id'] for item in query.dicts()})
        return map_zone_location_mapping.get(origin_port_id),map_zone_location_mapping.get(destination_port_id)
    
    def find_statistics_object(self, identifier):
        freight = (
            FclFreightRateStatistic.select()
            .where(
                FclFreightRateStatistic.identifier == identifier
            )
            .first()
        )
        return freight
    
    def find_rate_object(self,id):
        freight = (
            FclFreightRate.select()
            .where(
                FclFreightRate.id == id
            )
            .first()
        )
        return freight
    
    
    def get_validity_params(self, validity):
        price = validity.get('price')
        line_items = validity.get('line_items')
        if not price and line_items:
            currency_lists = [item["currency"] for item in line_items if item["code"] == "BAS"]
            currency = currency_lists[0]
            if len(set(currency_lists)) != 1:
                price = float(sum(common.get_money_exchange_for_fcl({"price": item.get('price') or item.get('buy_price'), "from_currency": item['currency'], "to_currency": currency}).get('price', 100) for item in line_items))
            else:
                price = float(sum(item.get('price') or item.get('buy_price') for item in line_items))   
            pass
            
        validity_details =  {
                "validity_created_at": validity.get('validity_start'),
                "validity_updated_at": validity.get('validity_start'),
                "price": price,
                "currency":validity.get("currency") or validity.get('freight_price_currency') or validity.get('freight_price_currency'),
                "payment_term":validity.get("payment_term") or DEFAULT_PAYMENT_TERM,
                "schedule_type":validity.get("schedule_type") or DEFAULT_SCHEDULE_TYPES ,
                "validity_start":validity.get("validity_start"),
                "validity_end":validity.get("validity_end")
            }
        return validity_details
    
    def get_spot_search_rates(self,offset = 0, limit = 10, return_count = False,):
        all_result = []
        try:
            newconnection = get_connection()  
            with newconnection:
                with newconnection.cursor() as cur:
                    if return_count:
                        sql = 'SELECT count(service_rates) as rate_obj FROM spot_search_rates, jsonb_array_elements(rate_cards) AS element, jsonb_each(element-> %s) AS service_rates WHERE service_rates.value->> %s is not null and  service_rates.value->> %s = %s'
                        cur.execute(sql, ('service_rates','rate_id','service_type','fcl_freight'))
                        result = cur.fetchone()[0]
                        return result
                    else:
                        sql = 'SELECT service_rates.value as rate_obj FROM spot_search_rates, jsonb_array_elements(rate_cards) AS element, jsonb_each(element-> %s) AS service_rates WHERE service_rates.value->> %s is not null and  service_rates.value->> %s = %s order by spot_search_rates.id limit %s offset %s'
                        cur.execute(sql, ('service_rates','rate_id','service_type','fcl_freight', limit, offset))
                    
                        result = cur.fetchall()
                        for res in result:
                            all_result.append(
                            res
                            )
                        cur.close()
            newconnection.close()
            return all_result
        except Exception as e:
            print('Error from railsDb', e)
            return all_result
    
    def get_imp_ext_id_from_spot_search_rates(self,source_id):
        total_result=[]
        newconnection = get_connection()
        with newconnection:
            with newconnection.cursor() as cursor:
                sql = 'SELECT importer_exporter_id AS imp_ext_id FROM spot_searches WHERE id = %s'
                cursor.execute(sql,source_id)
                result=cursor.fetchall()
                for res in result:
                    total_result.append(
                    res
                    )
        cursor.close()
        return total_result       
class PopulateFclFreightRateStatistics(MigrationHelpers):
    def __init__(self) -> None:
        self.cogoback_connection = get_connection()
    
    def populate_active_rate_ids(self):
        query = FclFreightRate.select().where(FclFreightRate.validities.is_null(False) and FclFreightRate.validities != '[]').order_by(FclFreightRate.id)
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
                    rate = json.loads(rate)['rate_obj']
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
            FclFreightRateStatistic.insert_many(row_data).execute()
            
                
                
    def populate_from_feedback(self):
        query = FclFreightRateFeedback.select(FclFreightRateFeedback.booking_params).distinct(FclFreightRateFeedback.fcl_freight_rate_id, FclFreightRateFeedback.validity_id).where(FclFreightRateFeedback.booking_params['rate_card']['price'].is_null(False))
        feedbacks = jsonable_encoder(list(query.dicts()))
        breakpoint()
        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())
            
        count = 0    
        actual_count = 0 
        row_data = []
               
        for feedback in feedbacks: 
            count+= 1
            print(count)
            
            rate_card = feedback['booking_params']['rate_card']
            identifier = '{}_{}'.format(rate_card['rate_id'], rate_card['validity_id'])
            
            statistics_obj = self.find_statistics_object(identifier)
            
            if statistics_obj:
                continue
            
            rate = self.find_rate_object(rate_card['rate_id'])
            
            if not rate:
                continue

            rate = model_to_dict(rate)
            
            rate_params = {key: rate.get(key) for key in RATE_PARAMS} 
            validity_params = self.get_validity_params(rate_card)
        
            row = {
                **rate_params, 
                **validity_params,
                "containers_count": rate.get("containers_count") or 0,
                'identifier' : identifier,
                'rate_id' : rate.get('id'),
                "rate_type": rate.get('rate_type') or DEFAULT_RATE_TYPE,
                "origin_region_id": REGION_MAPPING.get(rate.get('origin_port_id')),
                "destination_region_id": REGION_MAPPING.get(rate.get('destination_port_id')),
                "rate_created_at": rate.get('created_at'),
                "rate_updated_at": rate.get('updated_at'),
                'validity_id' : rate_card['validity_id'],
                "market_price": rate_card.get('market_price') or validity_params.get('price'),
            }
            
            row_data.append(row)
            actual_count+= 1
            if len(row_data) >= 10 or len(feedback) == count:
                FclFreightRateStatistic.insert_many(row_data).execute()
                row_data = []

    def populate_feedback_fcl_freight_rate_statistic(self):
        query = FclFreightRateFeedback.select()
        feedbacks = jsonable_encoder(list(query.dicts()))
        count = 0    
        row_data = []
               
        for feedback in feedbacks: 
            count+= 1
            
            identifier = '{}_{}'.format(feedback['rate_id'], feedback['validity_id'])

            statistics_obj = self.find_statistics_object(identifier)
            
            if statistics_obj:
                if (feedback['feedback_type']=='liked'):
                    setattr(statistics_obj, 'likes_count', statistics_obj.likes_count+1)
                elif(feedback['feedback_type']=='disliked'):
                    setattr(statistics_obj, 'dislikes_count', statistics_obj.dislikes_count+1)
                saved_status = statistics_obj.save()
                if not saved_status:
                    print("! Error: Couldn't save statistics_obj", statistics_obj.id)
                else:
                    print('Saved ...',statistics_obj.id)
                continue
            
        
            row = {
                "feedback_id": feedback.get('id'),
                "validity_id" : feedback.get('validity_id'),
                "rate_id" : feedback.get('fcl_freight_rate_id'),
                "source" : feedback.get('source'),
                "source_id" : feedback.get('source_id'),
                "performed_by_id" : feedback.get('performed_by_id'),
                "performed_by_org_id" : feedback.get('performed_by_org_id'),
                "created_at": feedback.get('created_at'),
                "updated_at": feedback.get('updated_at'),
                "importer_exporter_id": feedback.get('importer_exporter_id'),
                "service_provider_id": feedback.get('service_provider_id'),
                "feedback_type":feedback.get('feedback_type'),
                "closed_by_id":feedback.get('closed_by_id'),
                "serial_id":feedback.get('serial_id'),
            }
            row_data.append(row)
            if len(row_data) >= 10 or len(feedback) == count:
                FeedbackFclFreightRateStatistic.insert_many(row_data).execute()
                row_data = []       
                
    def populate_from_spot_search(self):
        total_count = self.get_spot_search_rates(return_count=True) or 0
        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())
                
        offset = 0
        count = 0
        while offset < total_count:
            row_data = []
            rate_cards = self.get_spot_search_rates(offset=offset,limit=BATCH_SIZE)
            offset += BATCH_SIZE
            
            for rate_card in rate_cards:
                identifier = '{}_{}'.format(rate_card['rate_id'], rate_card['validity_id'])
                statistics_obj = self.find_statistics_object(identifier)
                
                if statistics_obj:
                    continue
                
                rate = self.find_rate_object(rate_card['rate_id'])
                
                if not rate:
                    continue
                
                rate = model_to_dict(rate)
                
                rate_params = {key: rate.get(key) for key in RATE_PARAMS} 
                validity_params = self.get_validity_params(rate_card)
            
                row = {
                    **rate_params, 
                    **validity_params,
                    'identifier' : identifier,
                    "containers_count": rate.get("containers_count") or 0,
                    'rate_id' : rate.get('id'),
                    "rate_type": rate.get('rate_type') or DEFAULT_RATE_TYPE,
                    "origin_region_id": REGION_MAPPING.get(rate.get('origin_port_id')),
                    "destination_region_id": REGION_MAPPING.get(rate.get('destination_port_id')),
                    "rate_created_at": rate.get('created_at'),
                    "rate_updated_at": rate.get('updated_at'),
                    'validity_id' : rate_card['validity_id'],
                    "market_price": rate_card.get('market_price') or validity_params.get('price'),
                }
                count+= 1
                row_data.append(row)  
                print(count)  
            FclFreightRateStatistic.insert_many(row_data).execute()
                
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
        

    def populate_fcl_request_statistics(self):
        try:
            rate_stats = FclFreightRateRequest.select().limit(1000)
            for rate_stat in rate_stats:
                print('id', rate_stat.id)
                params = {
                    'origin_port_id':rate_stat.origin_port_id,
                    'destination_port_id':rate_stat.destination_port_id,
                    # 'origin_region_id':,
                    # 'destination_region_id':, ?? location api
                    'origin_country_id':rate_stat.origin_country_id,
                    'destination_country_id':rate_stat.destination_country_id,
                    'origin_continent_id':rate_stat.origin_continent_id,
                    'destination_continent_id':rate_stat.destination_continent_id,
                    'origin_trade_id':rate_stat.origin_trade_id,
                    'destination_trade_id':rate_stat.destination_trade_id,
                    # 'origin_pricing_zone_map_id':, ?? post_fcl_freight_helper ... get_pricing_map_zone_ids ?? fcl_frieght_location_cluster / mapping tables 
                    # 'destination_pricing_zone_map_id':, ?? use them to take map_zone_id 
                    'rate_request_id': rate_stat.id,
                    # 'validity_ids':, ?? MS TEAMS
                    'source': rate_stat.source,
                    'source_id': rate_stat.source_id,
                    'performed_by_id': rate_stat.performed_by_id,
                    'performed_by_org_id': rate_stat.performed_by_org_id,
                    'created_at': rate_stat.created_at,
                    'updated_at': rate_stat.updated_at,
                    'container_size':rate_stat.container_size,
                    'commodity':rate_stat.commodity,
                    'containers_count':rate_stat.containers_count,
                    # 'importer_exporter_id': ?? if(source='%spot%) then soruce_id = spot_search_id (foreign key) {spot_searches, spot_searches_fcl_freight_rate_Service} somewhere there is importteer-exporter-id ,
                    'closing_remarks': rate_stat.closing_remarks,
                    'closed_by_id': rate_stat.closed_by_id,
                    'request_type': rate_stat.request_type,
                }

                FclFreightRateRequestStatistic.create(**params)

        except Exception as e:
            print('! Exception:',e)


def main():
    populate_from_rates = PopulateFclFreightRateStatistics()
    # populate_from_rates.populate_active_rate_ids()
    # populate_from_rates.populate_from_feedback()
    # populate_from_rates.populate_from_spot_search()
    populate_from_rates.populate_fcl_request_statistics()

if __name__ == '__main__':   
    main()
