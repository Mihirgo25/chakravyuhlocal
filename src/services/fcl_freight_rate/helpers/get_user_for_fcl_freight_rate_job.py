from services.fcl_freight_rate.models.fcl_freight_rate_jobs import FclFreightRateJob
from peewee import fn

def get_user_for_fcl_freight_rate_job(users):
    query = (FclFreightRateJob.select(FclFreightRateJob.user_id, fn.Count(FclFreightRateJob.user_id).alias('user_id_count'))
         .where((FclFreightRateJob.user_id << users) &
                (FclFreightRateJob.status.not_in(['completed', 'aborted'])))
         .group_by(FclFreightRateJob.user_id)
         .order_by(fn.Count(FclFreightRateJob.user_id)))
    
    results = list(query.dicts())
    
    if results:
        return results[0]['user_id'].hex
    else:
        return None