from database.db_session import db
from services.trailer_freight_rates.models.trailer_freight_rate_estimator_constant import TrailerFreightRateCharges
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
from services.haulage_freight_rate.models.wagon_types import WagonTypes
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_cfs_rate.models.fcl_cfs_audits import FclCfsRateAudits
def create_table():
    # db.connect()
    try:
        db.create_tables([FclCfsRate,FclCfsRateAudits])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
