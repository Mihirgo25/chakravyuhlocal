from services.envision.models.ftl_rate_prediction_feedback import FtlRatePredictionFeedback
from database.db_session import db
from libs.logger import logger

def create_ftl_freight_rate_feedback(result):
    with db.atomic() as transaction:
        try:
            for feedback in result:
                row = {
                    'origin_location_id' : feedback.get('origin_location_id'),
                    'destination_location_id' : feedback.get('destination_location_id'),
                    'origin_region_id' : feedback.get('origin_region_id'),
                    'destination_region_id' : feedback.get('destination_region_id'),
                    'truck_type' : feedback.get('truck_type'),
                    'validity_start' : feedback.get('validity_start'),
                    'validity_end' : feedback.get('validity_end'),
                    'predicted_price_currency' : 'INR',
                    'predicted_price' : feedback.get('predicted_price') if 'predicted_price' in feedback else None,
                    'actual_price' : feedback.get('actual_price') if 'actual_price' in feedback else None,
                    'actual_price_currency' : feedback.get('actual_price_currency') if 'actual_price_currency' in feedback else None
                }

                new_rate = FtlRatePredictionFeedback.create(**row)
                feedback['id'] = new_rate.id

            return result
        except Exception as e:
            logger.error(e,exc_info=True)
            transaction.rollback()
            return "Creation Failed"