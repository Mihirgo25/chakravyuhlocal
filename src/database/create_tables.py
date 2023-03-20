from database.db_session import db
# from services.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit


from services.fcl_freight_rate.models.fcl_freight_rate_mapping import FclFreightRateMappings
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
def create_table():
    # db.connect()
    try:
        db.create_tables([FclFreightRateFreeDay])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()