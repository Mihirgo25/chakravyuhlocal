from database.db_session import db
from services.trailer_freight_rates.models.trailer_freight_rate_estimator_constant import TrailerFreightRateCharges

def create_table():
    # db.connect()
    try:
        db.create_tables([TrailerFreightRateCharges])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
