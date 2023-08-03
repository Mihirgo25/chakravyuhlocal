from database.rails_db import get_connection
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.bramhastra.models.air_freight_rate_statistic import AirFreightRateStatistic
from services.bramhastra.models.checkout_air_freight_rate_statistic import CheckoutAirFreightRateStatistic
from services.bramhastra.models.feedback_air_freight_rate_statistic import FeedbackAirFreightRateStatistic
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.bramhastra.models.air_freight_rate_request_statistics import AirFreightRateRequestStatistic
from services.bramhastra.models.shipment_air_freight_rate_statistic import ShipmentAirFreightRateStatistic
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE, DEFAULT_SCHEDULE_TYPES, DEFAULT_PAYMENT_TERM
from fastapi.encoders import jsonable_encoder
from micro_services.client import common
from playhouse.shortcuts import model_to_dict
from database.db_session import db
import urllib
import json

STANDARD_WEIGHT_SLABS=[
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
RATE_PARAMS = ["commodity","destination_continent_id", "destination_country_id", "destination_airport_id", "destination_trade_id", "origin_country_id", "origin_continent_id", "origin_airport_id", "origin_trade_id", "service_provider_id", "airline_id", "accuracy", "cogo_entity_id", "sourced_by_id", "procured_by_id", "stacking_type", "shipment_type", "operation_type","rate_type","price_type"]
class MigrationHelpers:
    def get_ll_and_ul(self,chargeable_weight):

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

    def find_rate_object(self, id):
        freight = AirFreightRate.select().where(AirFreightRate.id == id).first()
        return freight
    
    def get_validity_params(self, validity):
        price = validity.get("price")
        line_items = validity.get("line_items")
        if not price and line_items:
            currency_lists = [
                item["currency"] for item in line_items if item["code"] == "BAS"
            ]
            currency = currency_lists[0]
            if len(set(currency_lists)) != 1:
                price = float(
                    sum(
                        common.get_money_exchange_for_fcl(
                            {
                                "price": item.get("price") or item.get("buy_price"),
                                "from_currency": item["currency"],
                                "to_currency": currency,
                            }
                        ).get("price", 100)
                        for item in line_items
                    )
                )
            else:
                price = float(
                    sum(
                        item.get("price") or item.get("buy_price", 0)
                        for item in line_items
                    )
                )
            pass

        validity_details = {
            "validity_created_at": validity.get("validity_start"),
            "validity_updated_at": validity.get("validity_start"),
            "price": price,
            "currency": validity.get("currency"),
            "validity_start": validity.get("validity_start"),
            "validity_end": validity.get("validity_end"),
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
                    result = cursor.fetchall()
                    result = {row[1]: row[0] for row in result}
                    print(result)
                    cursor.close()
            newconnection.close()
        except Exception as e:
            print('Error from railsDB',e)
            return result    
                
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
            rate_cards = self.get_spot_search_rates_join(offset=offset, limit=100)
            # breakpoint()
            print(rate_cards)
            offset += 100

            for rate_card in rate_cards:
                weight = self.get_chargeable_weight(rate_card.get('volume', 0),rate_card.get('weight', 0))
                # breakpoint()
                statistics_obj = self.find_statistics_object(rate_card['rate_obj'].get('rate_id',0),rate_card['rate_obj'].get('validity_id',0),weight)
                print(statistics_obj)
                if statistics_obj:
                    continue

                rate = self.find_rate_object(rate_card["rate_obj"]["rate_id"])

                if not rate:
                    continue

                rate = model_to_dict(rate)

                rate_params = {key: rate.get(key) for key in RATE_PARAMS}
                validity_params = self.get_validity_params(rate_card['rate_obj'])

                row = {
                    **rate_params,
                    **validity_params,
                    "identifier": "",
                    "rate_id": rate.get("id"),
                    "rate_type": rate.get("rate_type") or DEFAULT_RATE_TYPE,
                    "origin_region_id": REGION_MAPPING.get(rate.get("origin_airport_id")),
                    "destination_region_id": REGION_MAPPING.get(
                        rate.get("destination_airport_id")
                    ),
                    "rate_created_at": rate.get("created_at"),
                    "rate_updated_at": rate.get("updated_at"),
                    "validity_id": rate.get("validity_id"),
                    "price": rate.get("market_price")
                    or validity_params.get("price"),
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
        
        for stat in query:
            stat.origin_pricing_zone_map_id = zone_ids[str(stat.origin_airport_port_id)]
            stat.destination_pricing_zone_map_id = zone_ids[str(stat.destination_airport_port_id)]
            stat.save()

    def update_air_freight_rate_checkout_count(self):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = '''SELECT 
                        cs.id, cs.weight, cs.volume, cs.rate, 
                        cs.checkout_id, cs.created_at, cs.updated_at, cs.status,
                        co.shipment_id, co.source_id
                        FROM checkout_air_freight_services AS cs
                        LEFT JOIN checkouts AS co 
                        ON cs.checkout_id = co.id
                        WHERE cs.rate ? 'rate_id' and cs.rate ? 'validity_id' 
                    '''
                cur.execute(sql)

                for row in cur:
                    limits = self.get_chargeable_weight(row[1], row[2])
                    rate_card = row[3]
                    if(
                        'rate_id' in rate_card and 'validity_id' in rate_card and 
                        rate_card['rate_id'] and rate_card['validity_id']
                    ):
                        identifier = '{}_{}_{}_{}'.format(rate_card['rate_id'], rate_card['validity_id'], limits[0], limits[1])

                        statistics = (
                            AirFreightRateStatistic.select()
                            .where(
                                AirFreightRateStatistic.identifier == identifier,
                                AirFreightRateStatistic.sign == 1,
                            )
                            .first()
                        )

                        if not statistics:
                            print("! Error: Identifier not present", identifier)
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
                            else:
                                self.populate_checkout_air_freight_statistics(row,rate_card['rate_id'],rate_card['validity_id'], identifier)

                cur.close()
        except Exception as e:
            print('! Exception:',e)
    
    def populate_checkout_air_freight_statistics( self, checkout_stats, rate_id, validity_id, identifier ):  
        try:
            params = {
                'checkout_air_freight_rate_services_id':checkout_stats[0],
                'checkout_id':checkout_stats[4],
                'created_at':checkout_stats[5],
                'updated_at':checkout_stats[6],
                'status':checkout_stats[7],
                'shipment_id':checkout_stats[8],
                'spot_search_id':checkout_stats[9],
                'rate_id':rate_id,
                'validity_id':validity_id,
            }

            if params["shipment_id"]:
                try:
                    self.populate_shipment_stats_in_air_freight_stats(rate_id, validity_id, params['shipment_id'], identifier)

                    quotation_ids = [None, None]
                    with self.cogoback_connection.cursor() as cur:
                        sql = f"SELECT id FROM shipment_buy_quotations where shipment_id = '{params['shipment_id']}'"
                        cur.execute(sql)
                        result = cur.fetchone()
                        if(result):
                            params['buy_quotation_id'] = result[0]
                            quotation_ids[0] = result[0]

                        sql = f"SELECT id FROM shipment_sell_quotations where shipment_id = '{params['shipment_id']}'"
                        cur.execute(sql)
                        result = cur.fetchone()
                        if(result):
                            params['sell_quotation_id'] = result[0]
                            quotation_ids[1] = result[0]
                        cur.close()

                        shipment_params = {
                            'shipment_id': params['shipment_id'],
                            'checkout_id': params['checkout_id'],
                            'spot_search_id': params['spot_search_id'],
                            'checkout_air_freight_rate_services_id': params['checkout_air_freight_rate_services_id'],
                            'buy_quotation_id': quotation_ids[0],
                            'sell_quotation_id': quotation_ids[1],
                            'rate_id':rate_id,
                            'validity_id':validity_id,
                        }

                except Exception as e:
                    print("! Exception occured while fetching shipment_quotations:", e)

            CheckoutAirFreightRateStatistic.create(**params)
            print("Saved ...")

        except Exception as e:
            print("! Exception occured while populating checkout stats:", e)

    def update_shipment_stats_in_air_freight_stats( self, rate_id, validity_id, shipment_id, identifier ):
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

                cur.close()

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
                            validity_ids = [item['id'] for item in result[0]]

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
            
    def populate_shipment_statistics(self, shipment_params):
        shipment_id = shipment_params['shipment_id']
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = '''SELECT sp.state, ssffs.id, 
                        sff.id, sff.cancellation_reason, sff.is_active,
                        sff.created_at, sff.updated_at
                        FROM shipments AS sp 
                        LEFT JOIN checkouts AS co ON co.shipment_id = sp.id 
                        LEFT JOIN spot_search_air_freight_services AS ssffs ON ssffs.spot_search_id = co.source_id
                        LEFT JOIN shipment_fcl_freight_services AS sff ON sff.shipment_id = sp.id 
                        WHERE sp.id = %s 
                    '''
                cur.execute(sql,(shipment_id))
                result = cur.fetchone()

                shipment_params['status'] = result[0]
                shipment_params['spot_search_air_freight_services_id'] = result[1]
                shipment_params['shipment_air_freight_rate_services_id'] = result[2]
                shipment_params['cancellation_reason'] = result[3]
                shipment_params['is_active'] = result[4]
                shipment_params['created_at'] = result[5]
                shipment_params['updated_at'] = result[6]
                
                ShipmentAirFreightRateStatistic.create(**shipment_params)

        except Exception as e:
            print('Exception:',e)

            
def main():
    populate_from_rates = PopulateAirFreightRateStatistics()
    # populate_from_rates.populate_from_active_rates()
    # populate_from_rates.populate_from_feedback()
    # populate_from_rates.populate_from_spot_search_rates()
    # populate_from_rates.populate_from_checkout_fcl_freight_rate_services()
    # populate_from_rates.update_shipment_stats_in_air_freight_stats()
    # populate_from_rates.update_air_freight_rate_checkout_count() 
    # populate_from_rates.populate_air_feedback_freight_rate_statistic()
    # populate_from_rates.populate_fcl_request_statistics()
    # populate_from_rates.update_accuracy()
    # populate_from_rates.update_fcl_freight_rate_statistics_spot_search_count()
    # populate_from_rates.update_pricing_map_zone_ids()
    pass


if __name__ == "__main__":
    main()
