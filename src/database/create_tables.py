from database.db_session import db
from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from services.air_customs_rate.models.air_customs_rate_bulk_operation import AirCustomsRateBulkOperation
from services.air_customs_rate.models.air_customs_rate_feedback import AirCustomsRateFeedback
from services.air_customs_rate.models.air_customs_rate_request import AirCustomsRateRequest


class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self,models):
        try:
            db.create_tables(models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = [AirCustomsRate, AirCustomsRateAudit,AirCustomsRateBulkOperation, AirCustomsRateFeedback, AirCustomsRateRequest]

    Table().create_tables(models)
