from database.db_session import db
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit
from services.chakravyuh.models.demand_transformation import DemandTransformation
from services.envision.models.haulage_rate_prediction_feedback import HaulageRatePredictionFeedback
from services.envision.models.ftl_rate_prediction_feedback import FtlRatePredictionFeedback
from services.envision.models.air_rate_prediction_feedback import AirFreightRatePredictionFeedback

def create_table():
    # db.connect()
    try:
        db.create_tables([FclFreightRateEstimation, FclFreightRateEstimationAudit, DemandTransformation])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
