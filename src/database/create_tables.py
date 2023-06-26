from database.db_session import db
from services.chakravyuh.models.air_freight_rate_estimation import AirFreightRateEstimation
from services.chakravyuh.models.air_freight_rate_estimation_audit import AirFreightRateEstimationAudit
from services.air_freight_rate.models.air_freight_location_cluster_factor import AirFreightLocationClusterFactor
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.haulage_freight_rate.models.haulage_freight_rate_request import HaulageFreightRateRequest
def create_table():
    # db.connect()
    try:
        db.create_tables([HaulageFreightRateRequest])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
