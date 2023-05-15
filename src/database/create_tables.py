from database.db_session import db
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit
from services.chakravyuh.models.demand_transformation import DemandTransformation
from services.chakravyuh.models.demand_transformation_audit import DemandTransformationAudit
from services.chakravyuh.models.revenue_target import RevenueTarget
from services.chakravyuh.models.revenue_target_audit import RevenueTargetAudit
from services.chakravyuh.models.fcl_freight_rate_local_estimation import FclFreightRateLocalEstimation
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.wagon_types import WagonTypes
def create_table():
    # db.connect()
    try:
        db.create_tables([HaulageFreightRateRuleSet, HaulageFreightRate, WagonTypes])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
