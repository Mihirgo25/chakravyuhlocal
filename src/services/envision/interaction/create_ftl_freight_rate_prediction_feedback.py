from database.db_session import db
from services.envision.models.fcl_rate_prediction_feedback import FtlRatePredictionFeedback
from micro_services.client import common

def create_ftl_freight_rate_prediction_feedback(result):
    for feedback in result:
        with db.atomic() as transaction:
            try:
                if "origin_region_id" not in feedback:
                    feedback["origin_region_id"] = None
                if "destination_region_id" not in feedback:
                    feedback["destination_region_id"] = None
                record = {
                    "origin_location_id": feedback.get("origin_location_id"),
                    "destination_location_id": feedback.get("destination_location_id"),
                    "origin_region_id": feedback.get("origin_region_id"),
                    "destination_region_id": feedback.get("destination_region_id"),
                    "origin_country_id": feedback.get("origin_country_id"),
                    "destination_country_id": feedback.get("destination_country_id"),
                    "truck_type":feedback.get('truck_type'),
                    "transit_time": feedback.get("transit_time"),
                    "validity_start": feedback.get("validity_start"),
                    "validity_end": feedback.get("validity_end"),
                    "predicted_price_currency": "USD",
                    "predicted_price": feedback.get('predicted_price'),
                    "actual_price": feedback.get("actual_price") if "actual_price" in feedback else None,
                    "actual_price_currency": feedback.get("actual_price_currency") if "actual_price_currency" in feedback else None,
                    "source" : feedback.get('source'),
                    "creation_id" : feedback.get("creation_id"),
                    "importer_exporter_id" : feedback.get('importer_exporter_id')
                }

                new_rate = FtlRatePredictionFeedback.create(**record)
                feedback['id'] = new_rate.id

                    # for val in result:
                    #     if ("predicted_price" in val) and val['predicted_price']:
                    #         val["predicted_price"] = round(common.get_money_exchange_for_fcl({'from_currency': "USD", 'to_currency': val["currency"], 'price': val["predicted_price"]})['price'])
                    # return result

            except:
                transaction.rollback()
                return {'success' : False}
    
    return {'success':True}