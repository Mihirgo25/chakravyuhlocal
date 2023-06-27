from database.db_session import db
from services.air_freight_rate.models.draft_air_freight_rate import DraftAirFreightRate
from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from services.fcl_customs_rate.models.fcl_customs_rate_bulk_operation import FclCustomsRateBulkOperation
from services.fcl_customs_rate.models.fcl_customs_rate_feedback import FclCustomsRateFeedback
from services.fcl_customs_rate.models.fcl_customs_rate_request import FclCustomsRateRequest
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
from services.fcl_cfs_rate.models.fcl_cfs_rate_bulk_operation import FclCfsRateBulkOperation
from services.fcl_cfs_rate.models.fcl_cfs_rate_request import FclCfsRateRequest
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from database.temp_audit_table import TempAudit


def create_table():
    # db.connect()
    try:
        db.create_tables([FclCustomsRate, FclCustomsRateAudit, FclCustomsRateBulkOperation,FclCustomsRateFeedback, FclCustomsRateRequest, FclCfsRate,FclCfsRateBulkOperation,FclCfsRateRequest, FclCfsRateAudit])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
