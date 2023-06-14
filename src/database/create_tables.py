from database.db_session import db
from services.air_freight_rate.models.draft_air_freight_rate import DraftAirFreightRate
def create_table():
    # db.connect()
    try:
        db.create_tables([DraftAirFreightRate])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
