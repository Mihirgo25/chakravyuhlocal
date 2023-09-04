from services.fcl_freight_rate.interaction.create_fcl_freight_rate_jobs import create_fcl_freight_rate_jobs
from services.air_freight_rate.interactions.create_air_freight_rate_jobs import create_air_freight_rate_jobs
from database.db_session import rd

current_processing_key = "spot_search_count"

def build_init_key(requirements, source):
    if source == 'fcl_freight':
        init_key = f'{str(requirements["origin_port_id"])}:{str(requirements["destination_port_id"])}:{str(requirements["container_size"])}:{str(requirements["container_type"])}:{str(requirements["commodity"] or "")}'
    elif source == 'air_freight':
        init_key = f'{str(requirements.get("origin_airport_id"))}:{str(requirements["destination_airport_id"] or "")}:{str(requirements["airline_id"])}:{str(requirements["commodity"])}:{str(requirements["commodity_type"] or "")}:{str(requirements.get("commodity_sub_type") or "")}::{str(requirements.get("stacking_type") or "")}:{str(requirements.get("operation_type") or "")}'
    return init_key


def get_current_predicted_count(requirements, source):
    if rd:
        try:
            cached_response = rd.hget(current_processing_key, build_init_key(requirements, source))
            return int(cached_response)
        except:
            return 0

def set_predicted_count(requirements, count, source):
    if rd:
        rd.hset(current_processing_key, build_init_key(requirements, source), int(count)+1)

def delete_init_key(requirements, source):
    rd.hdel([build_init_key(requirements, source)])


def spot_search_scheduler(is_predicted, requirements, source):
    if is_predicted:
        current_count = get_current_predicted_count(requirements, source)
        if current_count>=3:
            if source == 'fcl_freight':
                data = create_fcl_freight_rate_jobs(requirements,  'spot_search')
            elif source == 'air_freight':
                data = create_air_freight_rate_jobs(requirements,  'spot_search')
            delete_init_key(requirements, source)
            return {"init_key": requirements}
        else:
            set_predicted_count(requirements, current_count, source)
            return {"init_key": requirements}
    else:
        current_count = get_current_predicted_count(requirements, source)
        if current_count:
            delete_init_key(requirements, source)
            return {"init_key": requirements}







