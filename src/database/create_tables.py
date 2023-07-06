from database.db_session import db
from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from services.haulage_freight_rate.models.haulage_freight_rate_bulk_operation import HaulageFreightRateBulkOperation
from services.haulage_freight_rate.models.haulage_freight_rate_feedback import HaulageFreightRateFeedback
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
def create_table():
    # db.connect()
    try:
        db.create_tables([HaulageFreightRateAudit, HaulageFreightRateRequest, HaulageFreightRateBulkOperation, HaulageFreightRateFeedback, HaulageFreightRate])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
