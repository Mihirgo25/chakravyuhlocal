from database.db_session import db
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit
from services.chakravyuh.models.demand_transformation import DemandTransformation
from services.chakravyuh.models.demand_transformation_audit import DemandTransformationAudit
from services.chakravyuh.models.revenue_target import RevenueTarget
from services.chakravyuh.models.revenue_target_audit import RevenueTargetAudit
from services.chakravyuh.models.fcl_freight_rate_local_estimation import FclFreightRateLocalEstimation
from services.trailer_freight_rates.models.trailer_freight_rate_constant import TrailerFreightRateCharges
from services.trailer_freight_rates.models.basic_trailer_rates import BasicTrailerRate

def create_table():
    # db.connect()
    try:
        db.create_tables([TrailerFreightRateCharges, BasicTrailerRate])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
