from database.db_session import db
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
from services.haulage_freight_rate.models.wagon_types import WagonTypes
def create_table():
    # db.connect()
    try:
        db.create_tables([HaulageFreightRateRuleSet, WagonTypes])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
