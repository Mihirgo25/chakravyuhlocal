import datetime
from services.envision.models.air_rate_prediction_feedback import AirFreightRatePredictionFeedback
from database.db_session import db
import datetime


def create_air_freight_rate_feedback(result):
    with db.atomic() as transaction:
        try:
            for feedback in result:
                row = {
                    'origin_airport_id' : feedback['origin_airport_id'],
                    'destination_airport_id' :feedback['destination_airport_id'],
                    'airline_id' : feedback['airline_id'],
                    'packages_count' :feedback.get('packages_count'),
                    'volume' : feedback.get('volume'),
                    'weight' :  feedback.get('weight'),
                    'date' : datetime.datetime.now(),
                    'shipment_type':feedback.get('shipment_type'),
                    'stacking_type':feedback.get('stacking_type'),
                    'commodity':feedback.get('commodity'),
                    "predicted_price_currency": "USD",
                    "predicted_price": feedback["predicted_price"] if "predicted_price" in feedback else None,
                    "actual_price": feedback["actual_price"] if "actual_price" in feedback else None,
                    "actual_price_currency": feedback["actual_price_currency"] if "actual_price_currency" in feedback else None
                    }

                new_rate = AirFreightRatePredictionFeedback.create(**row)
                feedback['id'] = new_rate.id

        except:
            transaction.rollback()
            raise