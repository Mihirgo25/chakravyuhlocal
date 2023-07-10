from database.db_session import db
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_factor import FclFreightLocationClusterFactor
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping

def create_table():
    # db.connect()
    try:
        db.create_tables([FclFreightLocationCluster, FclFreightLocationClusterFactor, FclFreightLocationClusterMapping])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise


if __name__ == "__main__":
    create_table()
