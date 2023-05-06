import datetime
from services.envision.models.air_rate_prediction_feedback import AirFreightRatePredictionFeedback
from database.db_session import db
from libs.logger import logger
from currency_converter import CurrencyConverter
import datetime


def create_air_freight_rate_feedback(result):
    with db.atomic() as transaction:
        try:
            for feedback in result:
                row = {
                    'origin_airport_id' : feedback['origin_airport_id'],
                    'destination_airport_id' :feedback['destination_airport_id'],
                    'airline_id' : feedback['airline_id'],
                    'packages_count' :feedback['packages_count'],
                    'volume' : feedback['volume'],
                    'weight' :  feedback['weight'],
                    'date' : feedback['date'],
                    "predicted_price_currency": "USD",
                    "predicted_price": feedback["predicted_price"] if "predicted_price" in feedback else None,
                    "actual_price": feedback["actual_price"] if "actual_price" in feedback else None,
                    "actual_price_currency": feedback["actual_price_currency"] if "actual_price_currency" in feedback else None
                    }

                new_rate = AirFreightRatePredictionFeedback.create(**row)
                feedback['id'] = new_rate.id

            c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)

            for val in result:
                if "predicted_price" in val:
                    val["predicted_price"] = round(c.convert(val["predicted_price"], "USD", val["currency"], date=datetime.datetime.now()))
            return result

        except:
            transaction.rollback()

