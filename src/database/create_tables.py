from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.models.fcl_freight_rate_mapping import FclFreightRateMappings
from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from services.fcl_freight_rate.models.fcl_freight_rate_local_request import FclFreightRateLocalRequest
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from services.rate_sheet.models.rate_sheet import RateSheet
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from database.temp_audit_table import TempAudit
from services.envision.models.fcl_rate_prediction_feedback import FclRatePredictionFeedback
from services.envision.models.haulage_rate_prediction_feedback import HaulageRatePredictionFeedback
from services.envision.models.ftl_rate_prediction_feedback import FtlRatePredictionFeedback
from services.envision.models.air_rate_prediction_feedback import AirFreightRatePredictionFeedback
from services.ftl_freight_rate.models.ftl_services_audit import FtlServiceAudit
from services.ftl_freight_rate.models.truck import Truck
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit
from services.chakravyuh.models.demand_transformation import DemandTransformation
from services.chakravyuh.models.demand_transformation_audit import DemandTransformationAudit
from services.chakravyuh.models.revenue_target import RevenueTarget
from services.chakravyuh.models.revenue_target_audit import RevenueTargetAudit
from services.chakravyuh.models.fcl_freight_rate_local_estimation import FclFreightRateLocalEstimation

def create_table():
    # db.connect()
    try:
        db.create_tables([FtlServiceAudit,Truck])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
