from database.rails_db import get_connection
# from configs.global_constants import DEFAULT_WEIGHT_SLABS
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic
from services.bramhastra.models.checkout_air_freight_rate_statistic import CheckoutAirFreightRateStatistic
from services.bramhastra.models.feedback_air_freight_rate_statistic import FeedbackAirFreightRateStatistic
from services.bramhastra.models.spot_search_air_freight_rate_statistic import SpotSearchAirFreightRateStatistic
from fastapi.encoders import jsonable_encoder
from micro_services.client import common
from playhouse.shortcuts import model_to_dict
from micro_services.client import common
import urllib
import json
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

DEFAULT_WEIGHT_SLABS=[
    {
        'lower_limit':0.0,
        'upper_limit':45,
        'tariff_price':0,
        'currency':'INR',
        'unit':'per_kg'
    },
    {
        'lower_limit':45.1,
        'upper_limit':100.0,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'

        },
    {
        'lower_limit':100.1,
        'upper_limit':300.0,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'

    },
    {
        'lower_limit':300.1,
        'upper_limit':500.0,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'

    },{
        'lower_limit':500.1,
        'upper_limit':1000.0,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'
    },{
        'lower_limit':1000.1,
        'upper_limit':10000,
        'currency':'INR',
        'tariff_price':0,
        'unit':'per_kg'
    }

]

BATCH_SIZE = 1000
AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO = 166.67
REGION_MAPPING_URL = 'https://cogoport-production.sgp1.digitaloceanspaces.com/0860c1638d11c6127ab65ce104606100/id_region_id_mapping.json'
RATE_PARAMS = [ "commodity", "commodity_type", "commodity_sub_type", "destination_continent_id", "destination_country_id", "destination_local_id", "destination_airport_id", "destination_trade_id", "origin_country_id", "origin_local_id", "origin_continent_id", "origin_airport_id", "origin_trade_id", "service_provider_id", "shipping_line_id", "mode", "accuracy", "cogo_entity_id", "sourced_by_id", "procured_by_id", "stacking_type", "shipment_type", "operation_type","rate_type","price_type"]
CANCELLATION_REASON_CHEAPER_RATE = [
    ['low','lower','cheap','cheaper','less','lesser','better', 'issue'],
    ['quot','price','amount','cost','offer']
]

CANCELLATION_REASON_LOW_RATE = [
    ['low','lower','less','lesser', 'issue'],
    ['rate','profit']
]
class MigrationHelpers:
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
    def find_statistics_object(self,rate_id,validity_id,chargeable_weight):
        freight = (
            AirFreightRateStatistic.select()
            .where(
                AirFreightRateStatistic.rate_id == rate_id,
                AirFreightRateStatistic.validity_id == validity_id,
                AirFreightRateStatistic.lower_limit >= chargeable_weight,
                AirFreightRateStatistic.upper_limit <= chargeable_weight
            )
            .first()
        )
        return freight
    
    def find_rate_object(self,id):
        freight = (
            AirFreightRate.select()
            .where(
                AirFreightRate.id == id
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
                price = float(sum(item.get('price') or item.get('buy_price',0) for item in line_items))   
            pass
            
        validity_details =  {
                "validity_created_at": validity.get('validity_start'),
                "validity_updated_at": validity.get('validity_start'),
                "price": price,
                "currency":validity.get("currency") or validity.get('freight_price_currency') or validity.get('freight_price_currency'),
                "validity_start":validity.get("validity_start"),
                "validity_end":validity.get("validity_end")
            }
        return validity_details

    def get_imp_ext_id_from_spot_search_rates(self, source_ids):
        result=[]
        try:
            newconnection = get_connection()
            with newconnection:
                with newconnection.cursor() as cursor:
                    source_ids = tuple(source_ids)
                    sql = 'SELECT importer_exporter_id AS imp_ext_id, id as source_id FROM spot_searches WHERE id in %s'
                    cursor.execute(sql, (source_ids,))
                    result = cursor.fetchall()
                    result = {row[1]: row[0] for row in result}
                    print(result)
                    cursor.close()
            newconnection.close()
        except Exception as e:
            print('Error from railsDB',e)
            return result    
                
        return result  
    
    def get_imp_ext_id_from_checkouts_rates(self, source_ids):
        newconnection = get_connection()
        with newconnection:
            with newconnection.cursor() as cursor:
                source_ids = tuple(source_ids)
                print(source_ids)
                sql = 'SELECT importer_exporter_id AS imp_ext_id, id as source_id FROM checkouts WHERE id in (%s)'
                cursor.execute(sql, (source_ids,))
                result = cursor.fetchall()
                print(result, 'result')
                result = {row[1]: row[0] for row in result}
        return result
    
    def get_chargeable_weight(self,volume,weight):
        volumetric_weight = volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
        if volumetric_weight > weight:
            chargeable_weight = round(volumetric_weight)
        else:
            chargeable_weight = round(weight)
        return chargeable_weight
    
    def get_validity_params(self, validity):
            
            
        validity_details =  {
                "validity_created_at": validity.get('validity_start'),
                "validity_updated_at": validity.get('validity_start'),
                "currency":validity.get("currency") ,
                "density_category": validity.get('density_category'),
                "validity_start":validity.get("validity_start"),
                "validity_end":validity.get("validity_end"),
                "max_density_weight": validity.get("max_density_weight"),
                "min_density_weight": validity.get("min_density_weight"),
                
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
                    if validity and len(validity)>0 and 'id' in validity and validity['id']:
                        validity_params = self.get_validity_params(validity)

                        for weight_slab in validity.get('weight_slabs'):
                            count+= 1
                            
                            # breakpoint()
                            
                            if weight_slab['lower_limit'] and weight_slab['upper_limit']: 
                            
                                identifier = '{}_{}_{}_{}'.format(rate['id'], validity['id'], weight_slab['lower_limit'], weight_slab['upper_limit'])
                                    
                                rate_params = {key: value for key, value in rate.items() if key in RATE_PARAMS} 
                                price = weight_slab.get('tariff_price')
                                row = {
                                    **rate_params, 
                                    **validity_params,
                                    'identifier' : identifier,
                                    'rate_id' : rate.get('id'),
                                    "rate_created_at": rate.get('created_at'),
                                    "rate_updated_at": rate.get('updated_at'),
                                    "price": price,
                                    "rate_type": rate.get('rate_type') or DEFAULT_RATE_TYPE,
                                    "origin_region_id": REGION_MAPPING.get(rate.get('origin_airport_id')),
                                    "destination_region_id": REGION_MAPPING.get(rate.get('destination_airport_id')),
                                    "validity_id" : validity.get('id'),
                                    "lower_limit": weight_slab['lower_limit'],
                                    "upper_limit": weight_slab['upper_limit']
                                    
                                }
                                row_data.append(row)
                                print(count)
            AirFreightRateStatistic.insert_many(row_data).execute()

    
    def populate_feedback_air_freight_rate_statistic(self):
        query = AirFreightRateFeedback.select()
        print(query.count())

        feedbacks = jsonable_encoder(list(query.dicts()))
        count =0
        row_data=[row['source_id'] for row in feedbacks if row['source'] == 'spot_search']
        
        print(row_data)

        
        for feedback in feedbacks:
            count+=1
            weight = self.get_chargeable_weight(feedback.get('booking_params', {}).get('volume', 0),feedback.get('booking_params',{}).get('weight', 0))
            
            statistics_obj = self.find_statistics_object(feedback.get('air_frieght_rate_id'),feedback.get('validity_id'),weight)
            # print(statistics_obj)
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
            
                if (feedback['source']=='spot_rates'or feedback['source']=='spot_search' or feedback['source']=='spot_booking'):
                    imp_exp_id = self.get_imp_ext_id_from_spot_search_rates(feedback['source_id'])
                elif(feedback['source']=='checkout'):
                    imp_exp_id = self.get_imp_ext_id_from_checkouts_rates(feedback['source_id'])
                elif(feedback['source']=='promotional' or feedback['source']=='predicted'):
                    imp_exp_id = None
                row = {
                    "air_freight_rate_statistic_id":statistics_obj.id,
                    "feedback_id": feedback.get('id'),
                    "validity_id" : feedback.get('validity_id'),
                    "rate_id" : feedback.get('air_freight_rate_id'),
                    "source" : feedback.get('source'),
                    "source_id" : feedback.get('source_id'),
                    "performed_by_id" : feedback.get('performed_by_id'),
                    "performed_by_org_id" : feedback.get('performed_by_org_id'),
                    "created_at": feedback.get('created_at'),
                    "updated_at": feedback.get('updated_at'),
                    "importer_exporter_id": imp_exp_id,
                    "service_provider_id": feedback.get('service_provider_id'),
                    "feedback_type":feedback.get('feedback_type'),
                    "closed_by_id":feedback.get('closed_by_id'),
                    "serial_id":feedback.get('serial_id'),
                }
                row_data.append(row)
        # importer_exporter_ids = self.get_imp_ext_id_from_checkouts_rates([row['source_id'] for row in feedbacks if row['source'] == 'checkout'])
        importer_exporter_ids=self.get_imp_ext_id_from_spot_search_rates([row['source_id'] for row in feedbacks if row['source'] == ['spot_search']])

        for row in row_data:
            row['importer_exporter_id'] = importer_exporter_ids.get(row['source_id'], None)
        FeedbackAirFreightRateStatistic.insert_many(row_data).execute()

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

    
    
    def update_air_freight_rate_statistics_spot_search_count(self, limit = 2, offset = 0):
        try:
            with self.cogoback_connection.cursor() as cur:

                #total_count = self.get_spot_search_rates(return_count=True) 
                total_count = 10000
                print(total_count)

                while offset < total_count:

                    offset+=2

                    sql = """SELECT subq.spot_search_id, subq.rate_obj, chk.id, cfrs.id, ssq.id, sbq.id, sh.id, ssffs.id,ssffs.weight,ssffs.volume
                            FROM
                            (
                            SELECT spot_search_id, service_rates.value as rate_obj
                            FROM spot_search_rates AS ssr, jsonb_array_elements(rate_cards) AS element, jsonb_each(element-> %s) AS service_rates
                            where service_rates.value->> %s is not null and  service_rates.value->> %s = %s order by ssr.id limit %s offset %s) AS subq
                            left join checkouts AS chk ON subq.spot_search_id = chk.source_id and chk.source = %s
                            left join shipments AS sh ON chk.shipment_id = sh.id
                            left join checkout_air_freight_services AS cfrs ON chk.id = cfrs.checkout_id
                            left join shipment_sell_quotations AS ssq ON ssq.shipment_id = sh.id
                            left join shipment_buy_quotations AS sbq ON sbq.shipment_id = sh.id 
                            left join spot_search_air_freight_services AS ssffs ON ssffs.spot_search_id = subq.spot_search_id

                            
                            """
                    
                    
                    cur.execute(sql, ('service_rates','rate_id','service_type','air_freight', limit, offset,'spot_search'))
                    
                    result = cur.fetchall()
                    print(result)
                    
                    row_data = []
                    count=0
                    for res in result:
                        count +=1
                        service_rate = res[1]
                        
                        rate_id = service_rate['rate_id']
                        validity_id = service_rate['validity_id']
                        
                        volume=float(res[8])
                        weight=float(res[9])
                        
                        print(volume)
                        print(weight)
                       
                        chargeable_weight = self.get_chargeable_weight(volume,weight)

                        
                        statistic = AirFreightRateStatistic.select().where(
                        AirFreightRateStatistic.lower_limit <= chargeable_weight,
                        AirFreightRateStatistic.upper_limit >= chargeable_weight,
                        AirFreightRateStatistic.rate_id == rate_id,
                        AirFreightRateStatistic.validity_id == validity_id
                        
                        ).first()
                        
 
                        if statistic:               
                            setattr(statistic, 'spot_search_count', statistic.spot_search_count+1)

                            saved_status = statistic.save()
                            if not saved_status:
                                print("! Error: Couldn't save statistics", statistic.id)
                            else:
                                print('Saved ...',statistic.id)
                        

                            statistic = model_to_dict(statistic)
                            ffrs_id = statistic.get('id')
                        


                            row = {
                                "air_freight_rate_statistic_id": ffrs_id,
                                "spot_search_id": res[0] ,
                                "spot_search_air_freight_services_id": res[7] ,
                                "checkout_id": res[2] ,
                                "checkout_air_freight_rate_services_id": res[3] ,
                                "validity_id": validity_id,
                                "rate_id": rate_id,
                                "sell_quotation_id": res[4],
                                "buy_quotation_id": res[5],
                                "shipment_id": res[6] ,
                            }
                            row_data.append(row)
                            print(count)

                            SpotSearchAirFreightRateStatistic.insert_many(row_data).execute()


                cur.close()

        except Exception as e:
            print('! _Exception:',e)


            
def main():
    populate_from_rates = PopulateAirFreightRateStatistics()
    populate_from_rates.populate_feedback_air_freight_rate_statistic()
    pass

if __name__ == '__main__':   
    main()