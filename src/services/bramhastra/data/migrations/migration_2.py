from database.rails_db import get_connection
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic
from services.bramhastra.models.checkout_air_freight_rate_statistic import CheckoutAirFreightRateStatistic
from services.bramhastra.models.feedback_air_freight_rate_statistic import FeedbackAirFreightRateStatistic
from services.bramhastra.models.feedback_air_freight_rate_statistic import SpotSearchAirFreightRateStatistic 
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.bramhastra.models.air_freight_rate_request_statistics import AirFreightRateRequestStatistic
from services.bramhastra.models.shipment_air_freight_rate_statistic import ShipmentAirFreightRateStatistic
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_RATE_TYPE, DEFAULT_MODE
from services.bramhastra.constants import STANDARD_WEIGHT_SLABS
from fastapi.encoders import jsonable_encoder
from micro_services.client import common
from playhouse.shortcuts import model_to_dict
from database.db_session import db
from peewee import *
import urllib
import json
import uuid

BATCH_SIZE = 1000
AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO = 166.67
REGION_MAPPING_URL = 'https://cogoport-production.sgp1.digitaloceanspaces.com/0860c1638d11c6127ab65ce104606100/id_region_id_mapping.json'
STANDARD_CURRENCY = 'USD'
RATE_PARAMS = [
    "origin_airport_id",
    "destination_airport_id",
    "origin_country_id",
    "destination_country_id",
    "origin_continent_id",
    "destination_continent_id",
    "origin_trade_id",
    "destination_trade_id",
    "airline_id",
    "service_provider_id",
    "commodity",
    "commodity_type",
    "commodity_sub_type",
    "operation_type",
    "shipment_type",
    "stacking_type",
    "origin_local_id",
    "destination_local_id",
    "surcharge_id",
    "cogo_entity_id",
    "price_type",
    "sourced_by_id",
    "procured_by_id",
]

class MigrationHelpers:
 

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

    def get_chargeable_weight(self, weight, volume):
        volumetric_weight = volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
        if volumetric_weight > weight:
            chargeable_weight = round(volumetric_weight)
        else:
            chargeable_weight = round(weight)
        return chargeable_weight
    
    def find_statistics_object(self, rate_id, validity_id, chargeable_weight):
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
    
    def get_weight_slabs_from_chargeable_weight(self, chargeable_weight):
        for item in STANDARD_WEIGHT_SLABS:
            if item['lower_limit'] <= chargeable_weight <= item['upper_limit']:
                return item['lower_limit'], item['upper_limit']
        return STANDARD_WEIGHT_SLABS[-1]['lower_limit'], STANDARD_WEIGHT_SLABS[-1]['upper_limit']

    def find_statistics_object_by_wav(self, rate_id, validity_id, weight, volume):
        chargeable_weight = self.get_chargeable_weight(weight, volume)
        return self.find_statistics_object(rate_id, validity_id, chargeable_weight)
    
    def find_rate_object(self, id):
        freight = AirFreightRate.select().where(AirFreightRate.id == id).first()
        return freight
    
    def get_identifier(self,rate_id, validity_id, lower_limit, upper_limit):
        return f'{rate_id}{validity_id}{lower_limit}{upper_limit}'.replace('-','')

    def get_validity_params(self, validity, price, currency=STANDARD_CURRENCY):
        line_items = validity.get('line_items')
        if not price and line_items:
            currency_list = [item['currency'] for item in line_items if item['code'] == 'BAS']
            currency = currency_list[0] if currency_list else line_items[0].get('currency') or STANDARD_CURRENCY
            
            price = price = float(sum(common.get_money_exchange_for_fcl({"price": item['price'], "from_currency": item['currency'], "to_currency": currency}).get('price', 100) for item in line_items))
            
        
        if currency == STANDARD_CURRENCY:
            standard_price = price
        else: 
            standard_price = common.get_money_exchange_for_fcl(
                            {
                                "price": price ,
                                "from_currency": currency,
                                "to_currency": STANDARD_CURRENCY,
                            }).get("price", price) 
            
        validity_details = {
            "density_category": validity.get('density_categoty'),
            "max_density_weight": validity.get('max_density_weight'),
            "min_density_weight": validity.get('min_density_weight'),
            "validity_end": validity.get('validity_end'),
            "validity_start": validity.get('validity_start'),
            "standard_price": standard_price,
            "price": price,
            "currency": currency,
        }
        
        return validity_details

    
    def get_spot_search_rates_join(
        self,
        offset=0,
        limit=10,
        return_count=False,
    ):
        all_result = []
        try:
            newconnection = get_connection()
            with newconnection:
                with newconnection.cursor() as cur:
                    if return_count:
                        sql = 'WITH subq as (SELECT spot_search_id,service_rates.value AS rate_obj FROM spot_search_rates,jsonb_array_elements(rate_cards) AS element,jsonb_each(element -> %s) AS service_rates WHERE service_rates.value ->> %s IS NOT NULL AND service_rates.value ->> %s = %s ) SELECT COUNT(*) FROM subq JOIN spot_search_air_freight_services ON subq.spot_search_id = spot_search_air_freight_services.spot_search_id'
                        cur.execute(sql, ('service_rates','rate_id','service_type','air_freight'))
                        all_result = cur.fetchone()[0]
                    else:
                        sql = 'WITH subq as (SELECT spot_search_id,service_rates.value AS rate_obj FROM spot_search_rates,jsonb_array_elements(rate_cards) AS element,jsonb_each(element -> %s) AS service_rates WHERE service_rates.value ->> %s IS NOT NULL AND service_rates.value ->> %s = %s )select subq.rate_obj, spot_search_air_freight_services.volume, spot_search_air_freight_services.weight from subq join spot_search_air_freight_services on subq.spot_search_id = spot_search_air_freight_services.spot_search_id order by spot_search_air_freight_services.id limit %s offset %s'
                        cur.execute(
                            sql,
                            (
                                "service_rates",
                                "rate_id",
                                "service_type",
                                "air_freight",
                                limit,
                                offset,
                            ),
                        )

                        result = cur.fetchall()
                        for res in result:
                            all_result.append({'rate_obj':res[0],'volume':res[1],'weight':res[2]})
                    cur.close()
            newconnection.close()
            return all_result
        except Exception as e:
            print("Error from railsDb", e)
            return all_result

    def get_imp_ext_id_from_spot_search_rates(self, source_ids):
        result=[]
        try:
            newconnection = get_connection()
            with newconnection:
                with newconnection.cursor() as cursor:
                    source_ids = tuple(source_ids)
                    sql = 'SELECT importer_exporter_id AS imp_ext_id, id as source_id FROM spot_searches WHERE id in %s'
                    cursor.execute(sql, (source_ids,))
                    result = cursor.fetchone()
                    cursor.close()
            newconnection.close()
            return result
        except Exception as e:
            print('Error from railsDB',e)
            return result    
                    
    def get_imp_ext_id_from_checkouts_rates(self, source_id):
        newconnection = get_connection()
        with newconnection:
            with newconnection.cursor() as cursor:
                sql = 'SELECT importer_exporter_id AS imp_ext_id FROM checkouts WHERE id = %s'
                cursor.execute(sql, (source_id,))
                result = cursor.fetchone()
        return result
    
    def get_chargeable_weight(self,weight, volume):
        volumetric_weight = volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
        if volumetric_weight > weight:
            chargeable_weight = round(volumetric_weight)
        else:
            chargeable_weight = round(weight)
        return chargeable_weight
    

class PopulateAirFreightRateStatistics(MigrationHelpers):
    def __init__(self) -> None:
        self.cogoback_connection = get_connection()

    def populate_from_active_rates(self):
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
                    for weight_slab in validity.get('weight_slabs'):
                            count+= 1
                            if weight_slab['lower_limit'] and weight_slab['upper_limit']: 

                                identifier = self.get_identifier(rate['id'], validity['id'], weight_slab['lower_limit'], weight_slab['upper_limit'])

                                rate_params = {key: value for key, value in rate.items() if key in RATE_PARAMS} 
                                price = weight_slab.get('tariff_price')
                                currency = weight_slab.get('currency') or validity.get('currency')
                                validity_params = self.get_validity_params(validity, price, currency)
                                row = {
                                    **rate_params, 
                                    **validity_params,
                                    'identifier' : identifier,
                                    'rate_id' : rate.get('id'),
                                    "rate_created_at": rate.get('created_at'),
                                    "rate_updated_at": rate.get('updated_at'),
                                    "price": price,
                                    "currency": currency,
                                    "rate_type": rate.get('rate_type') or DEFAULT_RATE_TYPE,
                                    "source": rate.get('source') or DEFAULT_MODE,
                                    "origin_region_id": REGION_MAPPING.get(rate.get('origin_airport_id')),
                                    "destination_region_id": REGION_MAPPING.get(rate.get('destination_airport_id')),
                                    "validity_id" : validity.get('id'),
                                    "lower_limit": weight_slab['lower_limit'],
                                    "upper_limit": weight_slab['upper_limit']
                                }
                                row_data.append(row)
                                print(count)
            AirFreightRateStatistic.insert_many(row_data).execute()
    
    def populate_from_spot_search_rates(self):
        total_count = self.get_spot_search_rates_join(return_count=True) or 0
        print(total_count)
        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())

        offset = 0
        count = 0
        while offset < total_count:
            row_data = []
            rate_cards = self.get_spot_search_rates_join(offset=offset,limit=BATCH_SIZE)
            offset += BATCH_SIZE

            for rate_card in rate_cards:
                weight = self.get_chargeable_weight(rate_card.get('volume', 0),rate_card.get('weight', 0))
                weight_slab = self.get_weight_slabs_from_chargeable_weight(weight)
                statistics_obj = self.find_statistics_object(rate_card['rate_obj'].get('rate_id',0),rate_card['rate_obj'].get('validity_id',0),weight)

                if statistics_obj:
                    continue

                rate = self.find_rate_object(rate_card["rate_obj"]["rate_id"])

                if not rate:
                    continue

                rate = model_to_dict(rate)
                identifier = self.get_identifier(rate_card['rate_obj']['rate_id'],rate_card['rate_obj']['validity_id'],weight_slab[0],weight_slab[1])
                rate_params = {key: rate.get(key) for key in RATE_PARAMS}
                validity_params = self.get_validity_params(rate_card['rate_obj'], None, None)

                row = {
                    **rate_params,
                    **validity_params,
                    "identifier": identifier,
                    "rate_id": rate.get("id"),
                    "rate_type": rate.get("rate_type") or DEFAULT_RATE_TYPE,
                    "source": rate.get('source') or DEFAULT_MODE,
                    "origin_region_id": REGION_MAPPING.get(rate.get("origin_airport_id")),
                    "destination_region_id": REGION_MAPPING.get(
                        rate.get("destination_airport_id")
                    ),
                    "rate_created_at": rate.get("created_at"),
                    "rate_updated_at": rate.get("updated_at"),
                    "validity_id": rate_card['rate_obj'].get("validity_id"),
                    "lower_limit":weight_slab[0],
                    "upper_limit":weight_slab[1]
                }
               
                count += 1
                row_data.append(row)
                print(count)
            AirFreightRateStatistic.insert_many(row_data).execute()

    def populate_air_feedback_freight_rate_statistic( self ):
        query = AirFreightRateFeedback.select()

        feedbacks = jsonable_encoder(list(query.dicts))
        count = 0 
        row_data=[]
        for feedback in feedbacks:
            count+=1
            weight = self.get_chargeable_weight(feedback.get('booking_params', {}).get('volume', 0),feedback.get('booking_params',{}).get('weight', 0))
            statistics_obj = self.find_statistics_object(feedback.get('air_freight_rate_id'),feedback.get('validity_id'),weight)
           
            if statistics_obj:
                if feedback["feedback_type"] == "liked":
                    setattr(
                        statistics_obj, "likes_count", statistics_obj.likes_count + 1
                    )
                elif feedback["feedback_type"] == "disliked":
                    setattr(
                        statistics_obj,
                        "dislikes_count",
                        statistics_obj.dislikes_count + 1,
                    )
                saved_status = statistics_obj.save()
                if not saved_status:
                    print("! Error: Couldn't save statistics_obj", statistics_obj.id)
                else:
                    print("Saved ...", statistics_obj.id)

                if (
                    feedback["source"] == "spot_rates"
                    or feedback["source"] == "spot_search"
                    or feedback["source"] == "spot_booking"
                ):
                    imp_exp_id = self.get_imp_ext_id_from_spot_search_rates(
                        feedback["source_id"]
                    )
                elif feedback["source"] == "checkout":
                    imp_exp_id = self.get_imp_ext_id_from_checkouts_rates(
                        feedback["source_id"]
                    )
                elif (
                    feedback["source"] == "promotional"
                    or feedback["source"] == "predicted"
                ):
                    imp_exp_id = None
                row = {
                    "air_freight_rate_statistic_id": statistics_obj.id,
                    "feedback_id": feedback.get("id"),
                    "validity_id": feedback.get("validity_id"),
                    "rate_id": feedback.get("air_freight_rate_id"),
                    "source": feedback.get("source"),
                    "source_id": feedback.get("source_id"),
                    "performed_by_id": feedback.get("performed_by_id"),
                    "performed_by_org_id": feedback.get("performed_by_org_id"),
                    "created_at": feedback.get("created_at"),
                    "updated_at": feedback.get("updated_at"),
                    "importer_exporter_id": imp_exp_id,
                    "service_provider_id": feedback.get("service_provider_id"),
                    "feedback_type": feedback.get("feedback_type"),
                    "closed_by_id": feedback.get("closed_by_id"),
                    "serial_id": feedback.get("serial_id"),
                }
                row_data.append(row)
        FeedbackAirFreightRateStatistic.insert_many(row_data).execute()
        
    
    def update_pricing_map_zone_ids(self):
        query  = AirFreightLocationClusters.select(AirFreightLocationClusterMapping.location_id,AirFreightLocationClusters.map_zone_id).join(AirFreightLocationClusterMapping)
        zone_ids = jsonable_encoder(list(query.dicts()))
        zone_ids = {row['location_id']: row['map_zone_id'] for row in zone_ids}
        
        query = AirFreightRateStatistic.select()
        count = 0
        print(query.count())
        for stat in query:
            stat.origin_pricing_zone_map_id = zone_ids[str(stat.origin_airport_port_id)]
            stat.destination_pricing_zone_map_id = zone_ids[str(stat.destination_airport_port_id)]
            stat.save()
            count+= 1
            print(count)
            
        print('statistics done, updating request...')
        count = 0
        query = AirFreightRateRequestStatistic.select()
        for stat in query:
            count +=1
            stat.origin_pricing_zone_map_id = zone_ids.get(str(stat.origin_airport_id))
            stat.destination_pricing_zone_map_id = zone_ids.get(str(stat.destination_airport_id))
            stat.save()
            print(count)

    def update_air_freight_rate_checkout_count(self):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = '''SELECT 
                        cs.id, cs.weight, cs.volume, cs.rate, 
                        cs.checkout_id, cs.created_at, cs.updated_at, cs.status,
                        co.shipment_id, co.source_id
                        FROM checkout_air_freight_services AS cs
                        JOIN checkouts AS co 
                        ON cs.checkout_id = co.id
                        WHERE cs.rate ? 'rate_id' and cs.rate ? 'validity_id' 
                    '''
                cur.execute(sql)

                for row in cur:
                    rate_card = row[3]
                    if(
                        'rate_id' in rate_card and 'validity_id' in rate_card and 
                        rate_card['rate_id'] and rate_card['validity_id']
                    ):

                        statistics = self.find_statistics_object_by_wav(rate_card['rate_id'], rate_card['validity_id'],row[1], row[2])

                        if not statistics:
                            print("! Error: Identifier not present")
                        else:
                            setattr(
                                statistics,
                                "checkout_count",
                                statistics.checkout_count + 1,
                            )
                            saved_status = statistics.save()
                            if not saved_status:
                                print(
                                    "! Error: Couldn't save statistics", statistics.id
                                )

                cur.close()
        except Exception as e:
            print('! Exception:',e)
    
    def update_shipment_stats_in_air_freight_stats( self ):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = """
                        WITH valid_checkouts AS 
                            (
                                SELECT co.shipment_id AS shipment_id, 
                                cs.weight AS weight, cs.volume AS volume, 
                                cs.rate ->> 'rate_id' AS rate_id, cs.rate ->> 'validity_id' AS validity_id
                                    FROM checkout_air_freight_services AS cs
                                            JOIN checkouts AS co 
                                                ON cs.checkout_id = co.id
                                                    WHERE cs.rate ? 'rate_id' and cs.rate ? 'validity_id' 
                                                    and cs.rate ->> 'rate_id' is not null
                                                    and cs.rate ->> 'validity_id' is not null
                            )
                        SELECT 
                        valid_checkouts.weight, valid_checkouts.volume, valid_checkouts.rate_id, valid_checkouts.validity_id,
                        shipments.state AS shipment_state,
                        shipment_services.state AS package_state, shipment_services.packages_count
                            FROM shipments
                                JOIN shipment_air_freight_services AS shipment_services 
                                    ON shipments.id = shipment_services.shipment_id
                                JOIN valid_checkouts
                                    ON shipments.id = valid_checkouts.shipment_id
                """
                cur.execute(sql)
                results = cur.fetchall()
                cur.close()

                cntr = 0
                for row in results:
                    weight = row[0]
                    volume = row[1]
                    rate_id = row[2]
                    validity_id = row[3]
                    shipment_state = row[4]
                    container_state = row[5]
                    packages_count = row[6]
                    print('_', end='')

                    statistic = self.find_statistics_object_by_wav(rate_id, validity_id, weight, volume)
                    
                    if statistic:
                        cntr += 1
                        print(cntr,end='')
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

                        if container_state == "confirmed_by_service_provider":
                            setattr(
                                statistic,
                                "shipment_confirmed_by_service_provider_count",
                                statistic.shipment_confirmed_by_service_provider_count + 1,
                            )
                        elif container_state == "awaiting_service_provider_confirmation":
                            setattr(
                                statistic,
                                "shipment_awaited_service_provider_confirmation_count",
                                statistic.shipment_awaited_service_provider_confirmation_count
                                + 1,
                            )
                        elif container_state == "init":
                            setattr(
                                statistic,
                                "shipment_init_count",
                                statistic.shipment_init_count + 1,
                            )
                        elif container_state == "flight_arrived":
                            setattr(
                                statistic,
                                "shipment_flight_arrived_count",
                                statistic.shipment_flight_arrived_count + 1,
                            )
                        elif container_state == "flight_departed":
                            setattr(
                                statistic,
                                "shipment_flight_departed_count",
                                statistic.shipment_flight_departed_count + 1,
                            )
                        elif container_state == "cargo_handed_over_at_origin":
                            setattr(
                                statistic,
                                "shipment_cargo_handed_over_at_origin_count",
                                statistic.shipment_cargo_handed_over_at_origin_count + 1,
                            )
                        elif container_state == "cargo_handed_over_at_destination":
                            setattr(
                                statistic,
                                "shipment_cargo_handed_over_at_destination_count",
                                statistic.shipment_cargo_handed_over_at_destination_count + 1,
                            )

                        saved_status = statistic.save()
                        if not saved_status:
                            print("! Error: Couldn't save statistics", statistic.id)
                        else:
                            print("Saved ...", statistic.id)

        except Exception as e:
            print('! Exception occured while populating shipment stats:',e)

    def populate_air_request_statistics( self ):
        try:
            rate_stats = AirFreightRateRequest.select()

            REGION_MAPPING = {}
            with urllib.request.urlopen(REGION_MAPPING_URL) as url:
                REGION_MAPPING = json.loads(url.read().decode())

            for rate_stat in rate_stats:
                print('id', rate_stat.id)
                
                zone_map_ids = self.get_pricing_map_zone_ids(str(rate_stat.origin_port_id), str(rate_stat.destination_port_id))

                importer_exporter_id = None
                if('spot' in rate_stat.source):
                    try:
                        with self.cogoback_connection.cursor() as cur:
                            sql = f"SELECT importer_exporter_id from spot_searches where id = '{rate_stat.source_id}'"
                            cur.execute(sql)
                            result = cur.fetchone()
                            if result:
                                importer_exporter_id = result[0]
                    except Exception as e:
                        print('!Exception', e)
                    
                validity_ids = None
                if (rate_stat.status=='inactive') and rate_stat.closing_remarks and ('rate_added' in rate_stat.closing_remarks):
                    try:
                        sql = """
                            with main_table as (
                                with outer_cte as (
                                    with cte as ( SELECT updated_at FROM air_freight_rate_audits where object_id = %s and data @> %s )
                                    SELECT object_id FROM air_freight_rate_audits, cte WHERE object_type = %s and CAST(created_at AS timestamp) <= CAST(cte.updated_at AS timestamp) 
                                    ORDER BY created_at DESC limit 5
                                )
                                Select * from air_freight_rates where id in ( select object_id from outer_cte ) 
                                and origin_airport_id = % s 
                                and destination_airport_id = % s 
                                and commodity = % s 
                                order by created_at 
                                limit 1
                            ) 
                            Select validities from main_table
                        """
                        cursor = db.execute_sql(sql, (
                            rate_stat.id,
                            '{"closing_remarks": ["rate_added"]}',
                            'AirFreightRate',
                            'missing_rate',
                            rate_stat.origin_airport_id,
                            rate_stat.destination_airport_id,
                            rate_stat.commodity,
                        ))
                        result = cursor.fetchone()
                        if result:
                            validity_ids = [uuid.UUID(item['id']) for item in result[0]]

                    except Exception as e:
                        print('!Exception', e)
                
                params = {
                    'origin_airport_id':rate_stat.origin_port_id,
                    'destination_airport_id':rate_stat.destination_port_id,
                    'origin_region_id': REGION_MAPPING.get(rate_stat.origin_port_id),
                    'destination_region_id': REGION_MAPPING.get(rate_stat.destination_port_id),
                    'origin_country_id':rate_stat.origin_country_id,
                    'destination_country_id':rate_stat.destination_country_id,
                    'origin_continent_id':rate_stat.origin_continent_id,
                    'destination_continent_id':rate_stat.destination_continent_id,
                    'origin_trade_id':rate_stat.origin_trade_id,
                    'destination_trade_id':rate_stat.destination_trade_id,
                    'origin_pricing_zone_map_id': zone_map_ids[0],
                    'destination_pricing_zone_map_id': zone_map_ids[1], 
                    'rate_request_id': rate_stat.id,
                    'validity_ids': validity_ids,
                    'source': rate_stat.source,
                    'source_id': rate_stat.source_id,
                    'performed_by_id': rate_stat.performed_by_id,
                    'performed_by_org_id': rate_stat.performed_by_org_id,
                    'importer_exporter_id': importer_exporter_id,
                    'closing_remarks': rate_stat.closing_remarks,
                    'closed_by_id': rate_stat.closed_by_id,
                    'request_type': rate_stat.request_type,
                    'commodity':rate_stat.commodity,
                    'commodity_type':rate_stat.commodity_type,
                    'commodity_sub_type':rate_stat.commodity_sub_type,
                    'created_at': rate_stat.created_at,
                    'updated_at': rate_stat.updated_at,
                    'container_size':rate_stat.container_size,
                    'containers_count':rate_stat.containers_count,
                }

                AirFreightRateRequestStatistic.create(**params)

        except Exception as e:
            print('! Exception:',e)
            
    def populate_shipment_statistics( self ):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = '''
                    SELECT 
                        checkouts.shipment_id AS shipment_id,
                        checkouts.id AS checkout_id,
                        checkouts.source_id AS spot_search_id,
                        spot_search_services.id AS spot_search_air_freight_services_id,
                        checkout_air_freight_services.id AS checkout_air_freight_rate_services_id,
                        buy_qoute.id AS buy_quotation_id,
                        sell_qoute.id AS sell_quotation_id,
                        checkout_air_freight_services.rate ->> 'rate_id' AS rate_id,
                        checkout_air_freight_services.rate ->> 'validity_id' AS validity_id,
                        shipments.state AS status,
                        shipment_services.id AS shipment_air_freight_rate_services_id,
                        shipment_services.cancellation_reason AS cancellation_reason,
                        shipment_services.is_active AS is_active,
                        shipment_services.created_at AS created_at,
                        shipment_services.updated_at AS updated_at
                            FROM checkouts 
                                JOIN checkout_air_freight_services AS checkout_air_freight_services
                                    ON checkouts.id = checkout_air_freight_services.checkout_id
                                JOIN shipments
                                    ON checkouts.shipment_id = shipments.id
                                LEFT JOIN spot_search_air_freight_services AS spot_search_services
                                    ON spot_search_services.spot_search_id = checkouts.source_id
                                LEFT JOIN shipment_air_freight_services AS shipment_services 
                                    ON shipment_services.shipment_id = shipments.id 
                                LEFT JOIN shipment_sell_quotations AS sell_qoute
                                    ON sell_qoute.shipment_id = checkouts.shipment_id
                                LEFT JOIN shipment_buy_quotations AS buy_qoute
                                    ON buy_qoute.shipment_id = checkouts.shipment_id
                                    
                                WHERE checkout_air_freight_services.rate ? 'rate_id' and checkout_air_freight_services.rate ? 'validity_id' 
                                    and checkout_air_freight_services.rate ->> 'rate_id' is not null
                                    and checkout_air_freight_services.rate ->> 'validity_id' is not null

                                ORDER BY checkouts.shipment_id
                                limit %s offset %s
                    '''
                BATCH_SIZE = 1000
                OFFSET = 0
                cur.execute(sql, (BATCH_SIZE, OFFSET))
                result = cur.fetchall()
                while len(result) > 0:
                    print(OFFSET)
                    OFFSET+=BATCH_SIZE
                    row_data = []
                    for row in result:
                        row_data.append({
                            'shipment_id':row[0],
                            'checkout_id':row[1],
                            'spot_search_id':row[2],
                            'spot_search_air_freight_services_id':row[3],
                            'checkout_air_freight_rate_services_id':row[4],
                            'buy_quotation_id':row[5],
                            'sell_quotation_id':row[6],
                            'rate_id':row[7],
                            'validity_id':row[8],
                            'status':row[9],
                            'shipment_air_freight_rate_services_id':row[10],
                            'cancellation_reason':row[11],
                            'is_active':row[12],
                            'created_at':row[13],
                            'updated_at':row[14],
                        })
                    ShipmentAirFreightRateStatistic.insert_many(row_data).execute()
                    cur.execute(sql, (BATCH_SIZE, OFFSET))
                    result = cur.fetchall()

        except Exception as e:
            print('Exception:',e)

    def update_air_freight_rate_statistics_spot_search_count(self, limit = BATCH_SIZE, offset = 0):
        try:
            with self.cogoback_connection.cursor() as cur:

                #total_count = self.get_spot_search_rates(return_count=True) 
                total_count = 10000
                print(total_count)

                while offset < total_count:

                    offset+=BATCH_SIZE

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
    populate_from_rates.populate_from_active_rates() # active rates from rms to main_statistics
    #X populate_from_rates.populate_from_feedback() # old rates from data in feedbacks to main_statistics
    populate_from_rates.populate_from_spot_search_rates() # old rates from spot_search_rates to main_statistics
    populate_from_rates.update_shipment_stats_in_air_freight_stats() # data from shipment_air_freight_services to main_statistics
    populate_from_rates.update_air_freight_rate_checkout_count()  # checkout_count increment using checkout_fcl_freight_services into main_statistics + pululate checkout statistcs
    populate_from_rates.populate_air_feedback_freight_rate_statistic() # like dislike count in main_statistics and populate feedback_statistics
    populate_from_rates.populate_air_request_statistics() # populate request_air_statistics table
    populate_from_rates.populate_shipment_statistics() # shipment_statistics data population
    #X populate_from_rates.update_accuracy() # update accuracy, deviation from shipment_buy_quotation
    #X populate_from_rates.update_air_freight_rate_statistics_spot_search_count() # populate SpotSearchAirFreightRateStatistic table and increase spot_search_count
    populate_from_rates.update_pricing_map_zone_ids()  # update map_zone_ids for main_statistics and missing_requests
    pass


if __name__ == "__main__":
    main()
