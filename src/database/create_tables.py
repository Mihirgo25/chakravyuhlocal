from database.db_session import db

from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from services.ftl_freight_rate.models.ftl_freight_rate_bulk_operation import FtlFreightRateBulkOperation
from services.ftl_freight_rate.models.ftl_freight_rate_request import FtlFreightRateRequest
from services.ftl_freight_rate.models.ftl_freight_rate_feedback import FtlFreightRateFeedback


class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self,models):
        try:
            db.execute_sql('CREATE SEQUENCE ftl_freight_rate_request_serial_id_seq START WITH 2775 INCREMENT BY 1 MINVALUE 0;')
            db.execute_sql('CREATE SEQUENCE ftl_freight_rate_feedback_serial_id_seq START WITH 2419 INCREMENT BY 1 MINVALUE 0;')
            db.create_tables(models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = [FtlFreightRate, FtlFreightRateAudit,FtlFreightRateBulkOperation, FtlFreightRateRequest, FtlFreightRateFeedback]

    Table().create_tables(models)
