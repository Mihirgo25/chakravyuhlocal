from database.db_session import db
from services.trailer_freight_rate.models.trailer_freight_rate_estimator_constant import TrailerFreightRateEstimatorConstant
def create_table():
    # db.connect()
    try:
        db.create_tables([TrailerFreightRateEstimatorConstant])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
