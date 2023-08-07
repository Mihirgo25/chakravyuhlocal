from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_factor import FclFreightLocationClusterFactor
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from services.bramhastra.models.fcl_freight_rate_request_statistics import FclFreightRateRequestStatistic
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import SpotSearchFclFreightRateStatistic
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import FeedbackFclFreightRateStatistic
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import ShipmentFclFreightRateStatistic
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import CheckoutFclFreightRateStatistic

def create_table():
    # db.connect()
    try:
        db.create_tables([FclFreightRateStatistic,FclFreightRateRequestStatistic,SpotSearchFclFreightRateStatistic,FeedbackFclFreightRateStatistic,CheckoutFclFreightRateStatistic,FclFreightLocationCluster,FclFreightLocationClusterFactor,
FclFreightLocationClusterMapping,ShipmentFclFreightRateStatistic])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise

if __name__ == "__main__":
    create_table()
