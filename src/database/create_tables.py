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
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_freight_rate_local_agent import FclFreightRateLocalAgent
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.rate_sheet.models.rate_sheet import RateSheet
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit

def create_table():
    # db.connect()
    try:
        db.create_tables([FclFreightRate, FclFreightRateLocal, FclFreightRateLocalAgent, FclFreightRateAudit, FclFreightRateMappings, FclFreightRateCommoditySurcharge, FclFreightRateSeasonalSurcharge, FclFreightRateLocalRequest, FclFreightRateFreeDay, FclFreightRateWeightLimit, FclServiceAudit, FclFreightRateRequest, RateSheet, RateSheetAudit])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
