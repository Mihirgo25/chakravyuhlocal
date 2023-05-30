from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from services.air_freight_rate.models.air_services_audit import AirServiceAudit



def create_table():
    # db.connect()
    try:
        db.create_tables([AirFreightRateSurcharge,AirServiceAudit])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
