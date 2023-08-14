from database.rails_db import get_connection
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from playhouse.shortcuts import model_to_dict
from fastapi.encoders import jsonable_encoder
from datetime import datetime,timedelta
from peewee import SQL
import math
from configs.fcl_freight_rate_constants import (
    DEFAULT_RATE_TYPE,
    DEFAULT_SCHEDULE_TYPES,
    DEFAULT_PAYMENT_TERM,
)
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic
)
from services.fcl_freight_rate.models.fcl_freight_location_cluster import (
    FclFreightLocationCluster,
)
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
)
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import (
    FclFreightRateFeedback,
)
from services.fcl_freight_rate.models.fcl_freight_rate_request import (
    FclFreightRateRequest,
)
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit

from database.rails_db import get_connection
from playhouse.shortcuts import model_to_dict
from micro_services.client import common
import urllib
import json
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from micro_services.client import maps
from database.db_session import db
import uuid

BATCH_SIZE = 1000
REGION_MAPPING_URL = "https://cogoport-production.sgp1.digitaloceanspaces.com/0860c1638d11c6127ab65ce104606100/id_region_id_mapping.json"
CANCELLATION_REASON_CHEAPER_RATE = [
    ["low", "lower", "cheap", "cheaper", "less", "lesser", "better", "issue"],
    ["quot", "price", "amount", "cost", "offer"],
]

CANCELLATION_REASON_LOW_RATE = [
    ["low", "lower", "less", "lesser", "issue"],
    ["rate", "profit"],
]
RATE_PARAMS = [
    "commodity",
    "container_size",
    "container_type",
    "destination_country_id",
    "destination_local_id",
    "destination_detention_id",
    "destination_main_port_id",
    "destination_port_id",
    "destination_trade_id",
    "origin_country_id",
    "origin_local_id",
    "origin_detention_id",
    "origin_demurrage_id",
    "destination_demurrage_id",
    "origin_main_port_id",
    "origin_port_id",
    "origin_trade_id",
    "service_provider_id",
    "shipping_line_id",
    "mode",
    "accuracy",
    "cogo_entity_id",
    "sourced_by_id",
    "procured_by_id",
]

STANDARD_CURRENCY = "USD"

class MigrationHelpers:
    def get_pricing_map_zone_ids(self, origin_port_id, destination_port_id) -> list:
        query = (
            FclFreightLocationCluster.select(
                FclFreightLocationClusterMapping.location_id,
                FclFreightLocationCluster.map_zone_id,
            )
            .join(FclFreightLocationClusterMapping)
            .where(
                FclFreightLocationClusterMapping.location_id.in_(
                    [origin_port_id, destination_port_id]
                )
            )
        )
        map_zone_location_mapping = jsonable_encoder(
            {item["location_id"]: item["map_zone_id"] for item in query.dicts()}
        )
        return map_zone_location_mapping.get(
            origin_port_id
        ), map_zone_location_mapping.get(destination_port_id)

    def find_statistics_object(self, identifier):
        freight = FclFreightRateStatistic.select().where(FclFreightRateStatistic.identifier == identifier).first()
        return freight

    def get_filtered_identifiers(self, identifier_ar):
        query = FclFreightRateStatistic.select(FclFreightRateStatistic.identifier).where(FclFreightRateStatistic.identifier.in_(identifier_ar))
        identifier_ar = [row['identifier'] for row in  list(query.dicts())]
        return identifier_ar
        
    def find_rate_object(self, id):
        freight = FclFreightRate.select().where(FclFreightRate.id == id).first()
        return freight
    
    def get_identifier(self, rate_id, validity_id):
        return f'{rate_id}{validity_id}'.replace('-', '')

    def get_validity_params(self, validity):
        price = validity.get("price")
        line_items = validity.get("line_items")
        currency = validity.get("currency") or validity.get("freight_price_currency") or validity.get("freight_price_currency") or STANDARD_CURRENCY
        
        if not price and line_items:
            currency_lists = [
                item["currency"] for item in line_items if item["code"] == "BAS"
            ]
            currency = currency_lists[0]
            if len(set(currency_lists)) != 1:
                price = 0
                for item in line_items:
                    try:
                       price +=  common.get_money_exchange_for_fcl(
                            {
                                "price": item.get("price") or item.get("buy_price"),
                                "from_currency": item["currency"],
                                "to_currency": currency,
                            }
                        ).get("price", 100)
                    except:
                        price += 100
                    
                
            else:
                price = float(
                    sum(
                        item.get("price") or item.get("buy_price", 100)
                        for item in line_items
                    )
                )
            pass
        
        if currency == STANDARD_CURRENCY:
            standard_price = price
        else:
            try:
                standard_price = common.get_money_exchange_for_fcl(
                                {
                                    "price": price,
                                    "from_currency": currency,
                                    "to_currency": STANDARD_CURRENCY,
                                }
                            ).get("price", price)
            except:
                standard_price = price
            
        
        
        
        validity_details = {
            "validity_created_at": validity.get("validity_start"),
            "validity_updated_at": validity.get("validity_start"),
            "price": price,
            "standard_price": standard_price,
            "currency": currency,
            "payment_term": validity.get("payment_term") or DEFAULT_PAYMENT_TERM,
            "schedule_type": validity.get("schedule_type") or DEFAULT_SCHEDULE_TYPES,
            "validity_start": validity.get("validity_start"),
            "validity_end": validity.get("validity_end"),
        }
        return validity_details

    def get_spot_search_rates(
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
                        sql = 'SELECT count(service_rates) as rate_obj FROM spot_search_rates, jsonb_array_elements(rate_cards) AS element, jsonb_each(element-> %s) AS service_rates WHERE service_rates.value->> %s is not null and service_rates.value->> %s is not null and service_rates.value->> %s is not null and  service_rates.value->> %s = %s'
                        cur.execute(sql, ('service_rates','rate_id','validity_id','validity_start','service_type','fcl_freight'))
                        all_result = cur.fetchone()[0]
                    else:
                        sql = "SELECT service_rates.value as rate_obj FROM spot_search_rates, jsonb_array_elements(rate_cards) AS element, jsonb_each(element-> %s) AS service_rates WHERE service_rates.value->> %s is not null and service_rates.value->> %s is not null and service_rates.value->> %s is not null and  service_rates.value->> %s = %s order by spot_search_rates.id limit %s offset %s"
                        cur.execute(
                            sql,
                            (
                                "service_rates",
                                "rate_id",
                                'validity_id',
                                'validity_start',
                                "service_type",
                                "fcl_freight",
                                limit,
                                offset,
                            ),
                        )

                        result = cur.fetchall()
                        for res in result:
                            all_result.append(res[0])
                    cur.close()
            newconnection.close()
            return all_result
        except Exception as e:
            print("Error from railsDb", e)
            return all_result
        
    def get_shipment_data_for_accuracy(self):
        all_result = []
        try:
            newconnection = get_connection()  
            with newconnection:
                with newconnection.cursor() as cur:
                    sql = '''
                        WITH subquery AS (
                        SELECT 
                            shipment_buy_quotations.shipment_id,
                            shipment_buy_quotations.total_price,
                            shipment_buy_quotations.currency, 
                            shipment_fcl_freight_services.container_size,
                            shipment_fcl_freight_services.container_type, 
                            shipment_fcl_freight_services.commodity 
                        FROM 
                            shipment_buy_quotations 
                        RIGHT JOIN 
                            shipment_fcl_freight_services 
                            ON shipment_fcl_freight_services.id = shipment_buy_quotations.service_id 
                        WHERE 
                            shipment_buy_quotations.service_type= %s 
                            AND shipment_buy_quotations.is_deleted != %s  
                        ORDER BY 
                            shipment_buy_quotations.created_at
                        )
                        SELECT 
                            sh.id AS shipment_id, 
                            ch_services.rate-> %s AS rate_id,
                            ch_services.rate-> %s AS validity_id,
                            subquery.total_price,
                            subquery.currency
                        FROM 
                            shipments sh 
                        RIGHT JOIN 
                            checkouts ch 
                        ON sh.id = ch.shipment_id 
                        RIGHT JOIN 
                            checkout_fcl_freight_services ch_services 
                        ON ch.id =  ch_services.checkout_id 
                        LEFT JOIN 
                            subquery 
                        ON sh.id = subquery.shipment_id
                        WHERE 
                            sh.state = %s 
                        AND sh.shipment_type = %s  
                        AND ch_services.container_size = subquery.container_size 
                        AND ch_services.container_type = subquery.container_type
                        AND ch_services.commodity = subquery.commodity
                        AND ch_services.rate->%s is not null
                        AND ch_services.rate->%s != %s
                        ORDER BY 
                            sh.created_at
                    '''
                    
                    cur.execute(sql, ('fcl_freight_service',True,'rate_id', 'validity_id','completed','fcl_freight','rate_id', 'rate_id', 'null'))
                    result = cur.fetchall()
                    for res in result:
                        all_result.append( {'shipment_id' : res[0],'rate_id': res[1], 'validity_id': res[2], 'total_price': res[3], 'currency': res[4]})
                    cur.close()
            newconnection.close()
            return all_result
        except Exception as e:
            print('Error from railsDb', e)
            return  []
        
    def get_shipment_service_fcl_freight_data_for_accuracy(self, exclude_shipment_ids=[None]):
        all_result = []
        try:
            newconnection = get_connection()
            with newconnection:
                with newconnection.cursor() as cur:
                    exclude_shipment_ids = tuple(exclude_shipment_ids)
                    sql = '''
                        WITH subquery AS (
                            SELECT 
                                shipment_buy_quotations.shipment_id,
                                shipment_buy_quotations.total_price,
                                shipment_buy_quotations.currency, 
                                shipment_fcl_freight_services.origin_port_id,
                                shipment_fcl_freight_services.destination_port_id,
                                shipment_fcl_freight_services.origin_main_port_id,
                                shipment_fcl_freight_services.destination_main_port_id,
                                shipment_fcl_freight_services.origin_country_id,
                                shipment_fcl_freight_services.destination_country_id,
                                shipment_fcl_freight_services.origin_continent_id,
                                shipment_fcl_freight_services.destination_continent_id,
                                shipment_fcl_freight_services.container_size,
                                shipment_fcl_freight_services.container_type, 
                                shipment_fcl_freight_services.commodity,
                                shipment_fcl_freight_services.shipping_line_id,
                                shipment_fcl_freight_services.service_provider_id
                            FROM 
                                shipment_buy_quotations 
                            RIGHT JOIN 
                                shipment_fcl_freight_services 
                                ON shipment_fcl_freight_services.id = shipment_buy_quotations.service_id 
                            WHERE 
                                shipment_buy_quotations.service_type= %s 
                                AND shipment_buy_quotations.is_deleted != %s  
                            ORDER BY 
                                shipment_buy_quotations.created_at
                            )
                            SELECT 
                                sh.created_at AS created_at,
                                subquery.total_price,
                                subquery.currency, 
                                subquery.origin_port_id,
                                subquery.destination_port_id,
                                subquery.origin_main_port_id,
                                subquery.destination_main_port_id,
                                subquery.origin_country_id,
                                subquery.destination_country_id,
                                subquery.origin_continent_id,
                                subquery.destination_continent_id,
                                subquery.container_size,
                                subquery.container_type, 
                                subquery.commodity,
                                subquery.shipping_line_id,
                                subquery.service_provider_id
                            FROM 
                                shipments sh 
                            LEFT JOIN 
                                subquery 
                            ON sh.id = subquery.shipment_id
                            WHERE 
                                sh.state =  %s
                            AND sh.id not in %s
                            AND sh.shipment_type = %s 
                            AND subquery.total_price is not null 
                            AND total_price != 0
                            ORDER BY 
                                sh.created_at
                    '''
                    cur.execute(sql, ('fcl_freight_service',True,'completed',exclude_shipment_ids, 'fcl_freight'))
                    result = cur.fetchall()
                    for res in result:
                        all_result.append({
                            'created_at': res[0],
                            'total_price': res[1],
                            'currency': res[2],
                            'origin_port_id': res[3],
                            'destination_port_id': res[4],
                            'origin_main_port_id': res[5],
                            'destination_main_port_id': res[6],
                            'origin_country_id': res[7],
                            'destination_country_id': res[8],
                            'origin_continent_id': res[9],
                            'destination_continent_id': res[10],
                            'container_size': res[11],
                            'container_type': res[12],
                            'commodity': res[13],
                            'shipping_line_id': res[14],
                            'service_provider_id': res[15]
                        })
                    cur.close()
            newconnection.close()
            return all_result
        except Exception as e:
            print("Error from railsDb", e)
            return all_result
        
    def get_imp_exp_id_mapping_from_spot_searches(self, source_ids = [None]):
        all_results = {}
        try:
            newconnection = get_connection()
            with newconnection:
                with newconnection.cursor() as cursor:
                    source_ids = tuple(source_ids)
                    sql = "SELECT id, importer_exporter_id AS imp_ext_id FROM spot_searches WHERE id in %s"
                    cursor.execute(sql, (source_ids,))
                    result = cursor.fetchall()
                    for res in result:
                        all_results[res[0]] = res[1]
                    cursor.close()
            newconnection.close()
            return all_results
        except Exception as e:
            print("Error from railsDb", e)
            return all_results
                

    def get_imp_exp_id_mapping_from_checkouts(self, source_ids=[None]):
        all_results = {}
        try:
            newconnection = get_connection()
            with newconnection:
                with newconnection.cursor() as cursor:
                    source_ids = tuple(source_ids)
                    sql = "SELECT id, importer_exporter_id AS imp_ext_id FROM checkouts WHERE id = %s"
                    cursor.execute(sql, (source_ids))
                    result = cursor.fetchall()
                    for res in result:
                        all_results[res[0]] = res[1]
                    cursor.close()
            newconnection.close()
            return all_results
        except Exception as e:
            print("Error from railsDb", e)
            return all_results


class PopulateFclFreightRateStatistics(MigrationHelpers):
    def __init__(self) -> None:
        self.cogoback_connection = get_connection()

    def populate_from_active_rates(self):
        query = FclFreightRate.select().where((FclFreightRate.validities.is_null(False)) & (FclFreightRate.validities != SQL("'[]'")))
        
        total_count = query.count()

        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())
        count = 0
        last_updated_at = None 
        last_updated_ids = None
        still_has_rates = total_count > 0 
        
        print(total_count, 'total---')
        offset = 0
        while still_has_rates:
            if not last_updated_at:
                rates = query.order_by(FclFreightRate.updated_at).limit(BATCH_SIZE)
            else:
                rates = query.where((FclFreightRate.updated_at >= last_updated_at) and (FclFreightRate.id.not_in(last_updated_ids))).order_by(FclFreightRate.updated_at).limit(BATCH_SIZE)
            
            if not rates.count():
                still_has_rates = False
                break
            
            offset += BATCH_SIZE
            row_data = []
            for rate in rates:
                    
                for validity in rate.validities:
                    count += 1

                    identifier = self.get_identifier(str(rate.id), validity["id"])

                    rate_params = {
                        key: getattr(rate, key) for key in RATE_PARAMS
                    }
                    
                    validity_params = self.get_validity_params(validity)

                    row = {
                        **rate_params,
                        **validity_params,
                        "containers_count": getattr(rate, "containers_count") or 0,
                        "identifier": identifier,
                        "rate_id": getattr(rate, "id"),
                        "rate_created_at": getattr(rate, "created_at"),
                        "rate_updated_at": getattr(rate, "updated_at"),
                        "rate_type": getattr(rate, "rate_type") or DEFAULT_RATE_TYPE,
                        "origin_region_id": REGION_MAPPING.get(
                            getattr(rate, "origin_port_id")
                        ),
                        "destination_region_id": REGION_MAPPING.get(
                            getattr(rate, "destination_port_id")
                        ),
                        "market_price": validity.get("market_price")
                        or validity.get("price"),
                        "validity_id": validity.get("id"),
                    }
                    row_data.append(row)
                    print(count)
            last_updated_at = rates[-1].updated_at
            last_updated_ids = []
            i = len(rates) - 1

            while i >= 0 and rates[i].updated_at == last_updated_at:
                last_updated_ids.append(str(rates[i].id))
                i -= 1
                                
            FclFreightRateStatistic.insert_many(row_data).execute()

    def populate_from_feedback(self):
        query = (
            FclFreightRateFeedback.select(FclFreightRateFeedback.booking_params,FclFreightRateFeedback.fcl_freight_rate_id, FclFreightRateFeedback.validity_id)
            .where(
                FclFreightRateFeedback.booking_params["rate_card"]["price"].is_null(
                    False
                ),
                FclFreightRateFeedback.booking_params["rate_card"]["validity_start"].is_null(
                    False
                ),
                FclFreightRateFeedback.booking_params["rate_card"]["validity_id"].is_null(
                    False
                )
            )
        ).order_by(FclFreightRateFeedback.created_at.desc())

        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())

        count = 0
        offset = 0
        total_count = query.count()
        print(total_count, '-->total_count')
        
        while offset < total_count:
            row_data = []
            
            feedbacks = query.limit(BATCH_SIZE).offset(offset)
            
            offset += BATCH_SIZE
            
            identifier_ar = [self.get_identifier(str(feedback.fcl_freight_rate_id), str(feedback.validity_id)) for feedback in feedbacks]
            identifier_ar = self.get_filtered_identifiers(identifier_ar)
            
            for feedback in feedbacks:

                count += 1
                print(count)
                rate_card = feedback.booking_params["rate_card"]
                identifier = self.get_identifier(str(feedback.fcl_freight_rate_id), str(feedback.validity_id))

                if identifier in identifier_ar:
                    continue

                rate = self.find_rate_object(str(feedback.fcl_freight_rate_id))

                if not rate:
                    continue

                rate = model_to_dict(rate)

                rate_params = {key: rate.get(key) for key in RATE_PARAMS}
                validity_params = self.get_validity_params(rate_card)

                row = {
                    **rate_params,
                    **validity_params,
                    "containers_count": rate.get("containers_count") or 0,
                    "identifier": identifier,
                    "rate_id": str(feedback.fcl_freight_rate_id),
                    "rate_type": rate.get("rate_type") or DEFAULT_RATE_TYPE,
                    "origin_region_id": REGION_MAPPING.get(rate.get("origin_port_id")),
                    "destination_region_id": REGION_MAPPING.get(
                        rate.get("destination_port_id")
                    ),
                    "rate_created_at": rate.get("created_at"),
                    "rate_updated_at": rate.get("updated_at"),
                    "validity_id": str(feedback.validity_id),
                    "market_price": rate_card.get("market_price")
                    or validity_params.get("price"),
                }

                row_data.append(row)
            FclFreightRateStatistic.insert_many(row_data).execute()
    
    def update_pricing_map_zone_ids(self):
        query  = FclFreightLocationCluster.select(FclFreightLocationClusterMapping.location_id,FclFreightLocationCluster.map_zone_id).join(FclFreightLocationClusterMapping)
        zone_ids = jsonable_encoder(list(query.dicts()))
        zone_ids = {row['location_id']: row['map_zone_id'] for row in zone_ids}

        query = (
            FclFreightRateStatistic
            .update(
                origin_pricing_zone_map_id=zone_ids.get((FclFreightRateStatistic.origin_main_port_id or FclFreightRateStatistic.origin_port_id)),
                destination_pricing_zone_map_id=zone_ids.get((FclFreightRateStatistic.destination_main_port_id or FclFreightRateStatistic.destination_port_id))
            )
            .where(
                True
            )
        )
        query.execute()
        
        print('statistics done, updating request...')      
        count = 0
        query = FclFreightRateRequestStatistic.select()
        for stat in query:
            count +=1
            stat.origin_pricing_zone_map_id = zone_ids.get(str(stat.origin_main_port_id or stat.origin_port_id))
            stat.destination_pricing_zone_map_id = zone_ids.get(str(stat.destination_main_port_id or stat.destination_port_id))
            stat.save()
            print(count)
            
        
    def populate_feedback_fcl_freight_rate_statistic(self):
        query = FclFreightRateFeedback.select(FclFreightRateFeedback.feedback_type, FclFreightRateFeedback.id, FclFreightRateFeedback.validity_id, FclFreightRateFeedback.fcl_freight_rate_id, FclFreightRateFeedback.source, FclFreightRateFeedback.source_id, FclFreightRateFeedback.performed_by_id, FclFreightRateFeedback.performed_by_org_id, FclFreightRateFeedback.created_at, FclFreightRateFeedback.updated_at, FclFreightRateFeedback.service_provider_id, FclFreightRateFeedback.closed_by_id, FclFreightRateFeedback.serial_id)
        total_count = query.count()
        print(total_count , 'total_count...')
        count = 0
        offset = 0
        
        while(offset < total_count):
            feedbacks = query.limit(BATCH_SIZE).offset(offset)

            offset += BATCH_SIZE
            row_data = []
            
            for feedback in feedbacks:
                count += 1
        
                print(count)
                
                identifier = self.get_identifier(
                    str(feedback.fcl_freight_rate_id), str(feedback.validity_id)
                )

                statistics_obj = self.find_statistics_object(identifier)

                if not statistics_obj:
                    continue
                
                if feedback.feedback_type == "liked":
                    statistics_obj.likes_count += 1
                    
                elif feedback.feedback_type == "disliked":
                    statistics_obj.dislikes_count += 1
                    
                    
                statistics_obj.save()

                row = {
                    "fcl_freight_rate_statistic_id": str(statistics_obj.id),
                    "feedback_id": str(feedback.id),
                    "validity_id": str(feedback.validity_id),
                    "rate_id": str(feedback.fcl_freight_rate_id),
                    "source": feedback.source,
                    "source_id": str(feedback.source_id) if feedback.source_id else None,
                    "performed_by_id": str(feedback.performed_by_id) if feedback.performed_by_id else None,
                    "performed_by_org_id": str(feedback.performed_by_org_id) if feedback.performed_by_org_id else None,
                    "created_at": feedback.created_at,
                    "updated_at": feedback.updated_at,
                    "service_provider_id": str(feedback.service_provider_id) if feedback.service_provider_id else None,
                    "feedback_type": feedback.feedback_type,
                    "closed_by_id": str(feedback.closed_by_id) if feedback.closed_by_id else None,
                    "serial_id": str(feedback.serial_id) if feedback.serial_id else None,
                }
                row_data.append(row)
                    
            spot_search_ids = [row['source_id'] for row in row_data if "spot" in row['source']]
            imp_exp_mapping = jsonable_encoder(self.get_imp_exp_id_mapping_from_spot_searches(spot_search_ids)) if spot_search_ids else {}
            checkout_ids = [row['source_id'] for row in row_data if row['source'] == 'checkout']
            imp_exp_mapping.update(jsonable_encoder(self.get_imp_exp_id_mapping_from_checkouts(checkout_ids)) if checkout_ids else {})
            
            for row in row_data:
                row['importer_exporter_id'] = imp_exp_mapping.get(row['source_id'], None)
            FeedbackFclFreightRateStatistic.insert_many(row_data).execute()
    
                
    def populate_from_spot_search_rates(self):
        total_count = self.get_spot_search_rates(return_count=True) or 0
        REGION_MAPPING = {}
        with urllib.request.urlopen(REGION_MAPPING_URL) as url:
            REGION_MAPPING = json.loads(url.read().decode())

        offset = 1005000
        count = 0
        print(total_count,'total rates...')
        while offset < total_count:
            row_data = []
            rate_cards = self.get_spot_search_rates(offset=offset, limit=BATCH_SIZE)
            offset += BATCH_SIZE
            identifier_ar = [self.get_identifier(rate_card["rate_id"], rate_card["validity_id"]) for rate_card in rate_cards]
            identifier_ar = self.get_filtered_identifiers(identifier_ar)
            
            rate_ids = [row['rate_id'] for row in rate_cards]
            fcl_freight_rates = FclFreightRate.select().where(FclFreightRate.id.in_(rate_ids))
            
            fcl_freight_rates = jsonable_encoder({row['id']: row for row in list(fcl_freight_rates.dicts())})

            for rate_card in rate_cards:
                identifier = self.get_identifier(
                    rate_card["rate_id"], rate_card["validity_id"]
                )

                if identifier in identifier_ar:
                    continue

                rate = fcl_freight_rates.get(rate_card["rate_id"])

                if not rate:
                    continue

                rate_params = {key: rate.get(key) for key in RATE_PARAMS}
                validity_params = self.get_validity_params(rate_card)

                row = {
                    **rate_params,
                    **validity_params,
                    "identifier": identifier,
                    "containers_count": rate.get("containers_count") or 0,
                    "rate_id": rate.get("id"),
                    "rate_type": rate.get("rate_type") or DEFAULT_RATE_TYPE,
                    "origin_region_id": REGION_MAPPING.get(rate.get("origin_port_id")),
                    "destination_region_id": REGION_MAPPING.get(
                        rate.get("destination_port_id")
                    ),
                    "rate_created_at": rate.get("created_at"),
                    "rate_updated_at": rate.get("updated_at"),
                    "validity_id": rate_card["validity_id"],
                    "market_price": rate_card.get("market_price")
                    or validity_params.get("price"),
                }
                
                count += 1
                print(count)
                row_data.append(row)
            FclFreightRateStatistic.insert_many(row_data).execute()
            
            print('offset->', offset,'\ncount->', count)

    def stem_words_using_nltk(self, sentence):
        words = word_tokenize(sentence)
        stemmer = PorterStemmer()
        stemmed_words = [stemmer.stem(word) for word in words]
        return stemmed_words

    def cancellation_reason_matching(self, stemmed_words, arr):
        flag = 0
        for word in arr[0]:
            if word in stemmed_words:
                flag = 1
        if flag == 1:
            for word in arr[1]:
                if word in stemmed_words:
                    flag += 1
        if flag > 1:
            return True
        return False

    def populate_shipment_stats_in_fcl_freight_stats(
        self, rate_id, validity_id, shipment_id
    ):
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

                identifier = self.get_identifier(rate_id, validity_id)
                statistic = (
                    FclFreightRateStatistic.select()
                    .where(
                        FclFreightRateStatistic.identifier == identifier,
                        FclFreightRateStatistic.sign == 1,
                    )
                    .first()
                )

                setattr(
                    statistic,
                    "containers_count",
                    statistic.containers_count + containers_count,
                )

                if shipment_state == "completed":
                    setattr(
                        statistic,
                        "shipment_completed_count",
                        statistic.shipment_completed_count + 1,
                    )
                elif shipment_state == "aborted":
                    setattr(
                        statistic,
                        "shipment_aborted_count",
                        statistic.shipment_aborted_count + 1,
                    )
                elif shipment_state == "in_progress":
                    setattr(
                        statistic,
                        "shipment_is_active_count",
                        statistic.shipment_is_active_count + 1,
                    )
                elif shipment_state == "shipment_received":
                    setattr(
                        statistic,
                        "shipment_awaited_service_provider_confirmation_count",
                        statistic.shipment_awaited_service_provider_confirmation_count
                        + 1,
                    )
                elif shipment_state == "confirmed_by_importer_exporter":
                    setattr(
                        statistic,
                        "shipment_confirmed_by_service_provider_countb",
                        statistic.shipment_confirmed_by_service_provider_countb + 1,
                    )
                elif shipment_state == "cancelled":
                    setattr(
                        statistic,
                        "shipment_cancelled_count",
                        statistic.shipment_cancelled_count + 1,
                    )

                    stem_words = self.stem_words_using_nltk(cancellation_reason)
                    if self.cancellation_reason_matching(
                        stem_words, CANCELLATION_REASON_CHEAPER_RATE
                    ):
                        setattr(
                            statistic,
                            "shipment_cancellation_reason_got_a_cheaper_rate_from_my_service_provider_count",
                            statistic.shipment_cancellation_reason_got_a_cheaper_rate_from_my_service_provider_count
                            + 1,
                        )
                    elif self.cancellation_reason_matching(
                        stem_words, CANCELLATION_REASON_LOW_RATE
                    ):
                        setattr(
                            statistic,
                            "shipment_booking_rate_is_too_low_count",
                            statistic.shipment_booking_rate_is_too_low_count + 1,
                        )

                if container_state == "containers_gated_out":
                    setattr(
                        statistic,
                        "shipment_containers_gated_out_count",
                        statistic.shipment_containers_gated_out_count + 1,
                    )
                elif container_state == "containers_gated_in":
                    setattr(
                        statistic,
                        "shipment_containers_gated_in_count",
                        statistic.shipment_containers_gated_in_count + 1,
                    )
                elif container_state == "init":
                    setattr(
                        statistic,
                        "shipment_init_count",
                        statistic.shipment_init_count + 1,
                    )
                elif container_state == "vessel_arrived":
                    setattr(
                        statistic,
                        "shipment_vessel_arrived_count",
                        statistic.shipment_vessel_arrived_count + 1,
                    )

                saved_status = statistic.save()
                if not saved_status:
                    print("! Error: Couldn't save statistics", statistic.id)
                else:
                    print("Saved ...", statistic.id)

                cur.close()

        except Exception as e:
            print("! Exception occured while populating shipment stats:", e)

    def populate_checkout_fcl_freight_statistics(
        self, checkout_stats, rate_id, validity_id
    ):
        try:
            params = {
                "checkout_fcl_freight_rate_services_id": checkout_stats[0],
                "checkout_id": checkout_stats[2],
                "created_at": checkout_stats[3],
                "updated_at": checkout_stats[4],
                "status": checkout_stats[5],
                "shipment_id": checkout_stats[6],
                "spot_search_id": checkout_stats[7],
                "rate_id": rate_id,
                "validity_id": validity_id,
            }

            if params["shipment_id"]:
                try:
                    self.populate_shipment_stats_in_fcl_freight_stats(
                        rate_id, validity_id, params["shipment_id"]
                    )
                    quotation_ids = [None, None]
                    with self.cogoback_connection.cursor() as cur:
                        sql = f"SELECT id FROM shipment_buy_quotations where shipment_id = '{params['shipment_id']}'"
                        cur.execute(sql)
                        result = cur.fetchone()
                        if result:
                            params["buy_quotation_id"] = result[0]
                            quotation_ids[0] = result[0]
                        
                        sql = f"SELECT id FROM shipment_sell_quotations where shipment_id = '{params['shipment_id']}'"
                        cur.execute(sql)
                        result = cur.fetchone()
                        if result:
                            params["sell_quotation_id"] = result[0]
                            quotation_ids[1] = result[0]
                        cur.close()

                except Exception as e:
                    print("! Exception occured while fetching shipment_quotations:", e)

            CheckoutFclFreightRateStatistic.create(**params)
            print("Saved ...")

        except Exception as e:
            print("! Exception occured while populating checkout stats:", e)

    def update_fcl_freight_rate_checkout_count(self):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = """SELECT 
                        cs.id, cs.rate, cs.checkout_id, cs.created_at, cs.updated_at, cs.status,
                        co.shipment_id, co.source_id
                        FROM checkout_fcl_freight_services AS cs
                        LEFT JOIN checkouts AS co 
                        ON cs.checkout_id = co.id
                        WHERE cs.rate ? 'rate_id'
                    """
                cur.execute(sql)

                for row in cur:
                    rate_card = row[1]
                    if (
                        "rate_id" in rate_card
                        and "validity_id" in rate_card
                        and rate_card["rate_id"]
                        and rate_card["validity_id"]
                    ):
                        identifier = self.get_identifier(
                            rate_card["rate_id"], rate_card["validity_id"]
                        )

                        statistics = (
                            FclFreightRateStatistic.select()
                            .where(
                                FclFreightRateStatistic.identifier == identifier,
                                FclFreightRateStatistic.sign == 1,
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
                                self.populate_checkout_fcl_freight_statistics(
                                    row, rate_card["rate_id"], rate_card["validity_id"]
                                )

                cur.close()
        except Exception as e:
            print("! Exception:", e)

    def update_fcl_freight_rate_statistics_spot_search_count(self, limit = BATCH_SIZE, offset = 0):
        try:
            with self.cogoback_connection.cursor() as cur:
                total_count = self.get_spot_search_rates(return_count=True)

                while offset < total_count:
                    offset += BATCH_SIZE

                    sql = """SELECT subq.spot_search_id, subq.rate_obj, chk.id, cfrs.id, ssq.id, sbq.id, sh.id, ssffs.id
                            FROM
                            (
                            SELECT spot_search_id, service_rates.value as rate_obj
                            FROM spot_search_rates AS ssr, jsonb_array_elements(rate_cards) AS element, jsonb_each(element-> %s) AS service_rates
                            where service_rates.value->> %s is not null and  service_rates.value->> %s = %s order by ssr.id limit %s offset %s) AS subq
                            left join checkouts AS chk ON subq.spot_search_id = chk.source_id and chk.source = %s
                            left join shipments AS sh ON chk.shipment_id = sh.id
                            left join checkout_fcl_freight_services AS cfrs ON chk.id = cfrs.checkout_id
                            left join shipment_sell_quotations AS ssq ON ssq.shipment_id = sh.id
                            left join shipment_buy_quotations AS sbq ON sbq.shipment_id = sh.id 
                            left join spot_search_fcl_freight_services AS ssffs ON ssffs.spot_search_id = subq.spot_search_id
                            """

                    cur.execute(
                        sql,
                        (
                            "service_rates",
                            "rate_id",
                            "service_type",
                            "fcl_freight",
                            limit,
                            offset,
                            "spot_search",
                        ),
                    )

                    result = cur.fetchall()
                    row_data = []

                    for res in result:
                        service_rate = res[1]

                        rate_id = service_rate["rate_id"]
                        validity_id = service_rate["validity_id"]

                        identifier = self.get_identifier(rate_id, validity_id)
                        statistic = self.find_statistics_object(identifier)

                        if statistic:
                            setattr(
                                statistic,
                                "spot_search_count",
                                statistic.spot_search_count + 1,
                            )

                            saved_status = statistic.save()
                            if not saved_status:
                                print("! Error: Couldn't save statistics", statistic.id)
                            else:
                                print("Saved ...", statistic.id)

                            statistic = model_to_dict(statistic)
                            ffrs_id = statistic.get("id")

                        row = {
                            "fcl_freight_rate_statistic_id": ffrs_id,
                            "spot_search_id": res[0],
                            "spot_search_fcl_freight_services_id": res[7],
                            "checkout_id": res[2],
                            "checkout_fcl_freight_rate_services_id": res[3],
                            "validity_id": validity_id,
                            "rate_id": rate_id,
                            "sell_quotation_id": res[4],
                            "buy_quotation_id": res[5],
                            "shipment_id": res[6],
                        }
                        row_data.append(row)

                    SpotSearchFclFreightRateStatistic.insert_many(row_data).execute()

                cur.close()

        except Exception as e:
            print("! _Exception:", e)

    def populate_fcl_request_statistics(self):
        try:
            rate_stats = FclFreightRateRequest.select()
            
            REGION_MAPPING = {}
            with urllib.request.urlopen(REGION_MAPPING_URL) as url:
                REGION_MAPPING = json.loads(url.read().decode())
                
            count = 0
            total_count = rate_stats.count()
            row_data = []
            for rate_stat in rate_stats:
                count+= 1
                importer_exporter_id = None
                if "spot" in rate_stat.source:
                    try:
                        with self.cogoback_connection.cursor() as cur:
                            sql = f"SELECT importer_exporter_id from spot_searches where id = '{rate_stat.source_id}'"
                            cur.execute(sql)
                            result = cur.fetchone()
                            if result:
                                importer_exporter_id = result[0]
                    except Exception as e:
                        print("!Exception", e)

                validity_ids = None
                if (rate_stat.status=='inactive') and rate_stat.closing_remarks and ('rate_added' in rate_stat.closing_remarks):
                    try:
                        sql = '''
                            with main_table as ( 
                                with outer_cte as ( 
                                    with cte as (  
                                        SELECT updated_at FROM fcl_freight_rate_audits 
                                            WHERE object_id = %s AND data @> %s 
                                    ) SELECT object_id FROM fcl_freight_rate_audits,cte 
                                        WHERE object_type= %s and source = %s 
                                        AND CAST(created_at AS timestamp) BETWEEN CAST(cte.updated_at AS timestamp) - INTERVAL '60 SECONDS'
                                        AND CAST(cte.updated_at AS timestamp) 
                                        ORDER BY created_at DESC limit 5 
                                ) Select * from fcl_freight_rates_temp  
                                    where id in (select object_id from outer_cte) 
                                    and origin_port_id = %s 
                                    and destination_port_id = %s 
                                    and commodity = %s  
                                    and container_type = %s 
                                    and container_size= %s 
                                    order by created_at limit 1 
                            ) Select validities, id from main_table 
                        '''
                        cursor = db.execute_sql(sql, (
                            rate_stat.id,
                            '{"closing_remarks": ["rate_added"]}',
                            'FclFreightRate',
                            'missing_rate',
                            rate_stat.origin_port_id,
                            rate_stat.destination_port_id,
                            rate_stat.commodity,
                            rate_stat.container_type,
                            rate_stat.container_size,
                        ))
                        result = cursor.fetchone()
                        if result and result[0]:
                            validity_ids = [uuid.UUID(item["id"]) for item in result[0]]

                    except Exception as e:
                        print("! Exception:", e)

                params = {
                    'origin_port_id':rate_stat.origin_port_id,
                    'destination_port_id':rate_stat.destination_port_id,
                    'origin_region_id': REGION_MAPPING.get(rate_stat.origin_port_id),
                    'destination_region_id': REGION_MAPPING.get(rate_stat.destination_port_id),
                    'origin_country_id':rate_stat.origin_country_id,
                    'destination_country_id':rate_stat.destination_country_id,
                    'origin_continent_id':rate_stat.origin_continent_id,
                    'destination_continent_id':rate_stat.destination_continent_id,
                    'origin_trade_id':rate_stat.origin_trade_id,
                    'destination_trade_id':rate_stat.destination_trade_id,
                    'rate_request_id': rate_stat.id,
                    'validity_ids': validity_ids,
                    'source': rate_stat.source,
                    'source_id': rate_stat.source_id,
                    'performed_by_id': rate_stat.performed_by_id,
                    'performed_by_org_id': rate_stat.performed_by_org_id,
                    'created_at': rate_stat.created_at,
                    'updated_at': rate_stat.updated_at,
                    'container_size':rate_stat.container_size,
                    'commodity':rate_stat.commodity,
                    'containers_count':rate_stat.containers_count,
                    'importer_exporter_id': importer_exporter_id,
                    'closing_remarks': rate_stat.closing_remarks,
                    'closed_by_id': rate_stat.closed_by_id,
                    'request_type': rate_stat.request_type,
                }
                row_data.append(params)
                
                print(count, len(row_data))
                if count == total_count or len(row_data) > BATCH_SIZE:
                    FclFreightRateRequestStatistic.insert_many(row_data).execute()
                    row_data = []

        except Exception as e:
            print("!! Exception:", e)

    def populate_shipment_statistics(self):
        try:
            with self.cogoback_connection.cursor() as cur:
                sql = '''
                    SELECT 
                        checkouts.shipment_id AS shipment_id,
                        checkouts.id AS checkout_id,
                        checkouts.source_id AS spot_search_id,
                        spot_search_services.id AS spot_search_fcl_freight_services_id,
                        checkout_fcl_freight_services.id AS checkout_fcl_freight_rate_services_id,
                        buy_qoute.id AS buy_quotation_id,
                        sell_qoute.id AS sell_quotation_id,
                        checkout_fcl_freight_services.rate ->> 'rate_id' AS rate_id,
                        checkout_fcl_freight_services.rate ->> 'validity_id' AS validity_id,
                        shipments.state AS status,
                        shipment_services.id AS shipment_fcl_freight_rate_services_id,
                        shipment_services.cancellation_reason AS cancellation_reason,
                        shipment_services.is_active AS is_active,
                        shipment_services.created_at AS created_at,
                        shipment_services.updated_at AS updated_at
                            FROM checkouts 
                                JOIN checkout_fcl_freight_services AS checkout_fcl_freight_services
                                    ON checkouts.id = checkout_fcl_freight_services.checkout_id
                                JOIN shipments
                                    ON checkouts.shipment_id = shipments.id
                                JOIN spot_search_fcl_freight_services AS spot_search_services
                                    ON spot_search_services.spot_search_id = checkouts.source_id
                                JOIN shipment_fcl_freight_services AS shipment_services 
                                    ON shipment_services.shipment_id = shipments.id 
                                LEFT JOIN shipment_sell_quotations AS sell_qoute
                                    ON sell_qoute.shipment_id = checkouts.shipment_id
                                LEFT JOIN shipment_buy_quotations AS buy_qoute
                                    ON buy_qoute.shipment_id = checkouts.shipment_id
                                    
                                WHERE checkout_fcl_freight_services.rate ? 'rate_id' and checkout_fcl_freight_services.rate ? 'validity_id' 
                                    and checkout_fcl_freight_services.rate ->> 'rate_id' is not null
                                    and checkout_fcl_freight_services.rate ->> 'validity_id' is not null

                                ORDER BY checkouts.shipment_id
                                limit %s offset %s
                    '''
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
                            'spot_search_fcl_freight_services_id':row[3],
                            'checkout_fcl_freight_rate_services_id':row[4],
                            'buy_quotation_id':row[5],
                            'sell_quotation_id':row[6],
                            'rate_id':row[7],
                            'validity_id':row[8],
                            'status':row[9],
                            'shipment_fcl_freight_rate_services_id':row[10],
                            'cancellation_reason':row[11],
                            'is_active':row[12],
                            'created_at':row[13],
                            'updated_at':row[14],
                        })
                    ShipmentFclFreightRateStatistic.insert_many(row_data).execute()
                    cur.execute(sql, (BATCH_SIZE, OFFSET))
                    result = cur.fetchall()
        except Exception as e:
            print('Exception:',e)
            
    
    def update_parent_rates(self):
        subquery = (FclFreightRateAudit
                    .select(FclFreightRateAudit.created_at, FclFreightRateFeedback.fcl_freight_rate_id.alias('fcl_freight_rate_id'), FclFreightRateFeedback.validity_id.alias('validity_id'),FclFreightRateFeedback.origin_port_id.alias('origin_port_id'),FclFreightRateFeedback.destination_port_id.alias('destination_port_id'),FclFreightRateFeedback.container_size.alias('container_size'), FclFreightRateFeedback.container_type.alias('container_type'), FclFreightRateFeedback.commodity.alias('commodity'))
                    .join(FclFreightRateFeedback, on=(FclFreightRateAudit.object_id  == FclFreightRateFeedback.id))
                    .join(FclFreightRate, on=(FclFreightRateFeedback.fcl_freight_rate_id == FclFreightRate.id))
                    .where((FclFreightRateAudit.object_type == 'FclFreightRateFeedback') & (FclFreightRateAudit.action_name == 'delete') & (FclFreightRate.mode == 'predicted'))
                    .order_by(FclFreightRateAudit.updated_at.desc()))
        
        main_query = (FclFreightRateAudit
                    .select(FclFreightRate.id.alias('rate_d'),FclFreightRate.origin_port_id.alias('origin_port_id'),FclFreightRate.destination_port_id.alias('destination_port_id'), FclFreightRate.container_size.alias('container_size'), FclFreightRate.container_type.alias('container_type'), FclFreightRate.commodity.alias('commodity'), FclFreightRateAudit.data['validity_start'].alias('validity_start'),FclFreightRateAudit.data['validity_end'].alias('validity_end') )
                    .join(FclFreightRate, on =(FclFreightRateAudit.object_id == FclFreightRate.id))
                    .where((FclFreightRateAudit.object_type == 'FclFreightRate') & (FclFreightRateAudit.action_name == 'create')))
        
        total_count = subquery.count()  
        print(total_count, 'total entries...')
        count = 0
        offset = 0
        while(offset < total_count):
            curquery = subquery.limit(BATCH_SIZE).offset(offset)
            offset += BATCH_SIZE
            
            main_row_data = jsonable_encoder(list(curquery.dicts()))
            
            for row in main_row_data:
                count+= 1
                print(count)
                audit = main_query.where(FclFreightRate.origin_port_id == row['origin_port_id'],
                FclFreightRate.destination_port_id == row['destination_port_id'],
                FclFreightRate.container_size == row['container_size'],
                FclFreightRate.container_type == row['container_type'],
                FclFreightRate.commodity == row['commodity'])
                
                audit = audit.where((FclFreightRateAudit.created_at <= row['created_at']) & (FclFreightRateAudit.created_at >= datetime.fromisoformat(row['created_at']) - timedelta(seconds = 5))).order_by(FclFreightRateAudit.created_at).limit(1)
                
                if not audit:
                    continue
                
                audit = jsonable_encoder(list(audit.dicts())[0])
                statistic_obj =  (
                        FclFreightRateStatistic.select()
                        .where((FclFreightRateStatistic.rate_id == row['fcl_freight_rate_id']) & (FclFreightRateStatistic.validity_start == audit['validity_start']) & (FclFreightRateStatistic.validity_end == audit['validity_end']))
                        .first()
                    )
                
                if not statistic_obj:
                    continue
                breakpoint()
                statistic_obj.parent_rate_id = row['fcl_freight_rate_id']
                statistic_obj.parent_validity_id = row['validity_id']
                statistic_obj.save()


    def update_accuracy(self):
        data = jsonable_encoder(self.get_shipment_data_for_accuracy())
        statistics_ids = []
        count = 0
        for row in data:
            identifier = self.get_identifier(row["rate_id"], row["validity_id"])
            statistics_obj = self.find_statistics_object(identifier)
            count+= 1
            print(count)
            if not statistics_obj:
                continue
            if not row['currency'] or row['currency'] == STANDARD_CURRENCY:
                total_price = row['total_price'] 
            else:
                try:
                    total_price = common.get_money_exchange_for_fcl(
                                {
                                    "price": row['total_price'] ,
                                    "from_currency": row['currency'],
                                    "to_currency": STANDARD_CURRENCY,
                                }).get("price", row['total_price'])
                except:
                    total_price = row['total_price']
                
            statistics_ids.append(str(statistics_obj.id))
            statistics_obj.booking_rate_count += 1
            statistics_obj.average_booking_rate = (statistics_obj.average_booking_rate + total_price)/ statistics_obj.booking_rate_count
            statistics_obj.accuracy = (1 - abs(statistics_obj.standard_price - total_price) / total_price) * 100
            statistics_obj.rate_deviation_from_latest_booking =  abs((statistics_obj.standard_price - total_price) / total_price) * 100
            statistics_obj.rate_deviation_from_booking_rate = abs((statistics_obj.standard_price - statistics_obj.average_booking_rate) / statistics_obj.average_booking_rate) * 100
            statistics_obj.save()
            
        
        shipment_ids = [str(row['shipment_id']) for row in data]
        
        data = jsonable_encoder(self.get_shipment_service_fcl_freight_data_for_accuracy(exclude_shipment_ids=shipment_ids))
        query = FclFreightRateStatistic.select().where(FclFreightRateStatistic.id.not_in(statistics_ids))
        
        for row in data:
            created_at = datetime.strptime(row.pop('created_at', None), '%Y-%m-%d')
            price = row.pop('total_price', None)
            currency = row.pop('currency', None)
            rate_query = query.where(**row)
            rate_query = rate_query.where(FclFreightRateStatistic.validity_start >= created_at,FclFreightRateStatistic.validity_end <= created_at )
            
            for statistics_obj in rate_query:
                if not currency or currency == STANDARD_CURRENCY:
                    total_price = price 
                else:
                    try:
                        total_price = common.get_money_exchange_for_fcl(
                                {
                                    "price": price ,
                                    "from_currency": currency,
                                    "to_currency": STANDARD_CURRENCY,
                                }).get("price", price)
                    except:
                        total_price = price
                    
                statistics_ids.append(str(statistics_obj.id))
                statistics_obj.average_booking_rate = (statistics_obj.average_booking_rate * statistics_obj.booking_rate_count + total_price)/ (statistics_obj.booking_rate_count + 1)
                statistics_obj.booking_rate_count += 1
                statistics_obj.accuracy = (1 - abs(statistics_obj.standard_price - total_price) / total_price) * 100
                statistics_obj.rate_deviation_from_latest_booking =  (statistics_obj.standard_price - total_price) / math.sqrt(statistics_obj.booking_rate_count)  
                statistics_obj.rate_deviation_from_booking_rate = (statistics_obj.standard_price - statistics_obj.average_booking_rate) / math.sqrt(statistics_obj.booking_rate_count)   
                statistics_obj.save()
                
            

def main():
    populate_from_rates = PopulateFclFreightRateStatistics()
    # print('# active rates from rms to main_statistics')
    populate_from_rates.populate_from_active_rates() 
    # print('# old rates from data in feedbacks to main_statistics')
    # populate_from_rates.populate_from_feedback() 
    # print('# old rates from spot_search_rates to main_statistics')
    # populate_from_rates.populate_from_spot_search_rates() 
    # print('# data from shipment_fcl_freight_services to main_statistics')
    # populate_from_rates.populate_shipment_stats_in_fcl_freight_stats() 
    # print('# checkout_count increment using checkout_fcl_freight_services into main_statistics + pululate checkout statistcs')
    # populate_from_rates.update_fcl_freight_rate_checkout_count() 
    # print('#like dislike count in main_statistics and populate feedback_statistics')
    # populate_from_rates.populate_feedback_fcl_freight_rate_statistic() 
    # print('#populate request_fcl_statistics table')
    # populate_from_rates.populate_fcl_request_statistics() 
    # print('#shipment_statistics data population')
    # populate_from_rates.populate_shipment_statistics() 
    # print('# update accuracy, deviation from shipment_buy_quotation')
    # populate_from_rates.update_accuracy() 
    # print('# populate SpotSearchFclFreightRateStatistic table and increase spot_search_count')
    # populate_from_rates.update_fcl_freight_rate_statistics_spot_search_count() 
    # print('# update map_zone_ids for main_statistics and missing_requests')
    # populate_from_rates.update_pricing_map_zone_ids() 
    # print('#update parent_rate_id and validity_id for reverted rates from feedback')
    # populate_from_rates.update_parent_rates() 


if __name__ == "__main__":
    main()
