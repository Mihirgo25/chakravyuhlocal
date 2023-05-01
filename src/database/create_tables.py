from database.db_session import db
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.chakravyuh.models.fcl_freight_rate_estimation_audit import FclFreightRateEstimationAudit
from services.chakravyuh.models.customer_transformations import CustomerTransformation

def create_table():
    # db.connect()
    try:
        db.create_tables([FclFreightRateEstimation, FclFreightRateEstimationAudit, CustomerTransformation])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
