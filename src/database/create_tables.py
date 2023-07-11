from database.db_session import db
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate

from services.ftl_freight_rate.models.ftl_freight_rate_request import FtlFreightRateRequest
def create_table():
    # db.connect()
    try:
        db.create_tables([FtlFreightRateRequest,FtlFreightRateAudit,FtlFreightRate])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
