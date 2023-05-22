from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_rate_properties import FclFreightRateProperties

def create_table():
    # db.connect()
    try:
        db.create_tables([FclFreightRateProperties])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
