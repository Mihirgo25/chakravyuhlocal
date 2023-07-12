from database.db_session import db
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from services.air_customs_rate.models.air_customs_rate_bulk_operation import AirCustomsRateBulkOperation
from services.air_customs_rate.models.air_customs_rate_feedback import AirCustomsRateFeedback
from services.air_customs_rate.models.air_customs_rate_request import AirCustomsRateRequest
from services.air_customs_rate.models.air_customs_rate import AirCustomsRate


def create_table():
    # db.connect()
    try:
        db.create_tables(
            [
                AirCustomsRateAudit,
                AirCustomsRateBulkOperation,
                AirCustomsRateFeedback,
                AirCustomsRateRequest,
                AirCustomsRate
            ]
        )
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise

if __name__ == "__main__":
    create_table()
