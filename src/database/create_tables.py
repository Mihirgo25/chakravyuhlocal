from database.db_session import db
from services.chakravyuh.models.air_freight_rate_estimation import AirFreightRateEstimation
from services.chakravyuh.models.air_freight_rate_estimation_audit import AirFreightRateEstimationAudit
from services.air_freight_rate.models.air_freight_location_cluster_factor import AirFreightLocationClusterFactor
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.trailer_freight_rates.models.trailer_freight_rate_estimator_constant import TrailerFreightRateCharges
from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
from services.haulage_freight_rate.models.wagon_types import WagonTypes
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedbacks
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_bulk_operation import AirFreightRateBulkOperation


def create_table():
    # db.connect()
    try:
        db.create_tables([AirFreightRate])
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise

if __name__ == "__main__":
    create_table()
