import datetime
from database.db_session import db
from libs.logger import logger
from services.envision.models.fcl_rate_prediction_feedback import FclRatePredictionFeedback
from currency_converter import CurrencyConverter
import datetime

def create_fcl_freight_rate_prediction_feedback(result):
    with db.atomic() as transaction:
        try:
            for feedback in result:
                if "origin_country_id" not in feedback:
                    feedback["origin_country_id"] = None
                if "destination_country_id" not in feedback:
                    feedback["destination_country_id"] = None
                record = {
                    "origin_port_id": feedback["origin_port_id"],
                    "destination_port_id": feedback["destination_port_id"],
                    "origin_country_id": feedback["origin_country_id"],
                    "destination_country_id": feedback["destination_country_id"],
                    "shipping_line_id": feedback["shipping_line_id"],
                    "container_size": feedback["container_size"],
                    "container_type": feedback["container_type"],
                    "commodity": feedback["commodity"],
                    "validity_start": feedback["validity_start"],
                    "validity_end": feedback["validity_end"],
                    "predicted_price_currency": "USD",
                    "predicted_price": feedback['line_items'][0]['price'] if ("line_items" in feedback) and (feedback['line_items']) else None,
                    "actual_price": feedback.get("actual_price") if "actual_price" in feedback else None,
                    "actual_price_currency": feedback.get("actual_price_currency") if "actual_price_currency" in feedback else None,
                    "source" : "predicted_for_rate_cards",
                    "creation_id" : feedback.get("creation_id"),
                    "importer_exporter_id" : feedback['importer_exporter_id']
                }

                new_rate = FclRatePredictionFeedback.create(**record)
                feedback['id'] = new_rate.id
                
            c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)

            for val in result:
                if ("predicted_price" in val) and val['predicted_price']:
                    val["predicted_price"] = round(c.convert(val["predicted_price"], "USD", val["currency"], date=datetime.datetime.now()))
            return result

        except:
            transaction.rollback()
            return {'success' : False}