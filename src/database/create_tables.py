from database.db_session import db
# from services.models.fcl_freight_rate import FclFreightRate
# from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit


# from services.fcl_freight_rate.models.fcl_freight_rate_locals import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_freight_rate_request import FclFreightRateRequest
from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback

def create_table():
    # db.connect()
    # try:
    query =  db.create_tables([FclFreightRateRequest])
    print(query)
    db.close()
    print("created table")
    # except:
    #     print("Exception while creating table")
    #     raise


if __name__ == "__main__":
    create_table()