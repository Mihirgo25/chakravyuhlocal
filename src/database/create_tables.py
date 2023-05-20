from database.db_session import db
from services.ftl_freight_rate.models.fuel_data import FuelData

def create_table():
    # db.connect()
    try:
        db.create_tables([FuelData])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
