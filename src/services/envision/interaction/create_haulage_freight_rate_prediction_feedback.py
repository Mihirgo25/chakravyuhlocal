from services.envision.models.haulage_rate_prediction_feedback import HaulageRatePredictionFeedback
from database.db_session import db
from libs.logger import logger

def create_haulage_freight_rate_feedback(result):
    with db.atomic() as transaction:
        try:
            for feedback in result:   
                row = {
                    'origin_location_id' : feedback.get('origin_location_id'),
                    'destination_location_id' : feedback.get('destination_location_id'),
                    'container_size' : feedback.get('container_size'),
                    'upper_limit' : feedback.get('upper_limit'),
                    'validity_start' : feedback.get('validity_start'),
                    'validity_end' : feedback.get('validity_end'),
                    'predicted_price_currency' : 'INR',
                    'predicted_price' : feedback.get('predicted_price') if 'predicted_price' in feedback else None,
                    'actual_price' : feedback.get('actual_price') if 'actual_price' in feedback else None,
                    'actual_price_currency' : feedback.get('actual_price_currency') if 'actual_price_currency' in feedback else None
                }

                new_rate = HaulageRatePredictionFeedback.create(**row)
                feedback['id'] = new_rate.id
            return result
        except Exception as e:
            logger.error(e,exc_info=True)
            transaction.rollback()
            return "Creation Failed"