from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate

def check_rate_availability(request):
    params = {
        "location_id": request["location_id"],
        "trade_type": request["trade_type"],
        "container_size": request["container_size"],
        "container_type": request["container_type"],
        "commodity": request["commodity"],
        "service_provider_id": request["service_provider_id"],
        "cargo_handling_type": request["cargo_handling_type"],
        "importer_exporter_id": request["importer_exporter_id"],
    }

    

















def create_fcl_cfs_rates(request):
    params = {
        "location_id": request["location_id"],
        # ""
    }
    kwargs = {
        # ""
    }

    create_rate = FclCfsRate.create(**kwargs)
    return True