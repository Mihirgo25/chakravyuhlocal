from database.db_session import db
from services.trailer_freight_rates.models.trailer_freight_rate_estimator_constant import TrailerFreightRateCharges
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
from services.haulage_freight_rate.models.wagon_types import WagonTypes
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
def create_table():
    # db.connect()
    try:
        # db.create_tables([TrailerFreightRateCharges, HaulageFreightRateRuleSet, WagonTypes])
        db.create_tables([AirFreightRateLocal])
    except:
        print("Exception while creating table")
        raise
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from services.air_freight_rate.models.air_freight_rate_feeback import AirFreightRateFeedbacks

# def create_table():
#     # db.connect()
#     try:
#         db.create_tables([AirFreightRateSurcharge,AirServiceAudit])
#         db.close()
def create_table():
    # db.connect()
    try:
        db.create_tables([AirFreightRateFeedbacks])
        db.close()

#         print("created table")
    except:
        print("Exception while creating table")
        raise

if __name__ == "__main__":
    create_table()
