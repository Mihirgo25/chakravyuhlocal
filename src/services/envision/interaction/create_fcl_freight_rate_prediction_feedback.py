from database.db_session import db
from services.envision.models.fcl_rate_prediction_feedback import FclRatePredictionFeedback
from micro_services.client import common

def create_fcl_freight_rate_prediction_feedback(result):
    for feedback in result:
        with db.atomic() as transaction:
            try:
                if "origin_country_id" not in feedback:
                    feedback["origin_country_id"] = None
                if "destination_country_id" not in feedback:
                    feedback["destination_country_id"] = None
                record = {
                    "origin_port_id": feedback.get("origin_port_id"),
                    "destination_port_id": feedback.get("destination_port_id"),
                    "origin_country_id": feedback.get("origin_country_id"),
                    "destination_country_id": feedback.get("destination_country_id"),
                    "origin_main_port_id":feedback.get('origin_main_port_id'),
                    "destination_main_port_id":feedback.get('destination_main_port_id'),
                    "shipping_line_id": feedback.get("shipping_line_id"),
                    "container_size": feedback.get("container_size"),
                    "container_type": feedback.get("container_type"),
                    "commodity": feedback.get("commodity"),
                    "validity_start": feedback.get("validity_start"),
                    "validity_end": feedback.get("validity_end"),
                    "predicted_price_currency": "USD",
                    "predicted_price": feedback['line_items'][0].get('price') if ("line_items" in feedback) and (feedback['line_items']) else None,
                    "actual_price": feedback.get("actual_price") if "actual_price" in feedback else None,
                    "actual_price_currency": feedback.get("actual_price_currency") if "actual_price_currency" in feedback else None,
                    "source" : feedback.get('source'),
                    "creation_id" : feedback.get("creation_id"),
                    "importer_exporter_id" : feedback.get('importer_exporter_id')
                }

                new_rate = FclRatePredictionFeedback.create(**record)
                feedback['id'] = new_rate.id

                # for val in result:
                #     if ("predicted_price" in val) and val['predicted_price']:
                #         val["predicted_price"] = round(common.get_money_exchange_for_fcl({'from_currency': "USD", 'to_currency': val["currency"], 'price': val["predicted_price"]})['price'])
                # return result

            except:
                transaction.rollback()
                return {'success' : False}