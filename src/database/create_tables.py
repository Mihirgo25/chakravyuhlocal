from database.db_session import db
from services.chakravyuh.models.cost_booking_estimation import CostBookingEstimation
from services.chakravyuh.models.cost_booking_estimation_audit import CostBookingEstimationAudit
def create_table():
    # db.connect()
    try:
        db.create_tables([CostBookingEstimation, CostBookingEstimationAudit])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
