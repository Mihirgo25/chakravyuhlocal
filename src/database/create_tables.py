from database.db_session import db
from services.trailer_freight_rates.models.trailer_freight_rate_estimator_constant import TrailerFreightRateCharges
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
from services.haulage_freight_rate.models.wagon_types import WagonTypes
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedbacks
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest

def create_table():
    # db.connect()
    try:
        # db.create_tables([FtlFreightRateRuleSet])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise

if __name__ == "__main__":
    create_table()
