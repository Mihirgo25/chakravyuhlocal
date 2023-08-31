from database.rails_db import get_most_searched_predicted_rates_for_fcl_freight_services
from micro_services.client import partner,maps
import copy
from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
from services.supply_tool.models.fcl_freight_rate_jobs_mapping import FclFreightRateJobsMapping
from datetime import datetime, timedelta
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects


def create_fcl_freight_rate_jobs(request):
    updated_ids = []
    for data in request:
        params = {
            'origin_port_id' : data.get('origin_port_id'),
            'origin_main_port_id' : data.get('origin_main_port_id'),
            'destination_port_id' : data.get('destination_port_id'),
            'destination_main_port_id' : data.get('destination_main_port_id'),
            'shipping_line_id' : data.get('shipping_line_id'),
            'service_provider_id' : data.get('service_provider_id'),
            'container_size' : data.get('container_size'),
            'container_type' : data.get('container_type'),
            'commodity' : data.get('commodity'),
            'source' : data.get('source'),
            'rate_type' : data.get('rate_type'),
        }
        if data.get('rate_id'):
            rate_id = data.get('rate_id')
        fcl_freight_rate_job = (FclFreightRateJobs.select().where(FclFreightRateJobs.rate_id == rate_id).first())

        if not fcl_freight_rate_job:
            fcl_freight_rate_job = FclFreightRateJobs(rate_id = rate_id)
            for key in list(params.keys()):
                setattr(fcl_freight_rate_job, key, params[key])
            
        if fcl_freight_rate_job.status in ('pending', 'backlog'):
            updated_ids.append(fcl_freight_rate_job.id)
            continue
        
        fcl_freight_rate_job.status = 'pending'
        fcl_freight_rate_job.save()
        get_multiple_service_objects(fcl_freight_rate_job)
        updated_ids.append(fcl_freight_rate_job.id)

    return {"updated_ids": updated_ids}
    