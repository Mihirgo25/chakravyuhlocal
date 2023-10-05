from services.air_freight_rate.models.air_freight_rate_jobs import AirFreightRateJob
from peewee import fn

def get_user_for_air_freight_rate_job(users):
    query = (AirFreightRateJob.select(AirFreightRateJob.user_id, fn.Count(AirFreightRateJob.user_id).alias('user_id_count'))
         .where((AirFreightRateJob.user_id << users) &
                (AirFreightRateJob.status.not_in(['completed', 'aborted'])))
         .group_by(AirFreightRateJob.user_id)
         .order_by(fn.Count(AirFreightRateJob.user_id)))
    
    results = list(query.dicts())
    
    if results:
        return str(results[0]['user_id'])
    else:
        return None