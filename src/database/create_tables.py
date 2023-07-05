from database.db_session import db
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from services.air_freight_rate.models.air_freight_rate_bulk_operation import AirFreightRateBulkOperation
from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.models.air_freight_rate_property import AirFreightRateProperty
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from services.air_freight_rate.models.air_freight_rate_tasks import AirFreightRateTasks
from services.air_freight_rate.models.air_freight_storage_rate import AirFreightStorageRates
from services.air_freight_rate.models.air_freight_warehouse_rate import AirFreightWarehouseRates
from services.air_freight_rate.models.air_services_audit import AirServiceAudit


def create_table():
    # db.connect()
    try:
        db.create_tables(
            [
                AirFreightRate,
                AirFreightRateAudit,
                AirFreightRateBulkOperation,
                AirFreightRateFeedback,
                AirFreightRateLocal,
                AirFreightRateProperty,
                AirFreightRateRequest,
                AirFreightRateSurcharge,
                AirFreightRateTasks,
                AirFreightStorageRates,
                AirFreightWarehouseRates,
                AirServiceAudit,
            ]
        )
        db.close()
        print("created table")
    except:
        print("Exception while creating table")
        raise

if __name__ == "__main__":
    create_table()
