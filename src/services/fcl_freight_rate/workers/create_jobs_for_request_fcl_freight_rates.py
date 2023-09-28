from services.fcl_freight_rate.interaction.create_fcl_freight_rate_job import (
    create_fcl_freight_rate_job,
)
def create_jobs_for_request_fcl_freight_rate(requirements):
    ids = create_fcl_freight_rate_job(requirements, "rate_request")
    return ids
