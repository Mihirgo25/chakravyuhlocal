from services.fcl_customs_rate.interaction.create_fcl_customs_rate_job import (
    create_fcl_customs_rate_job,
)
from database.db_session import rd

current_processing_key = "spot_search_count_fcl_customs"


def build_init_key(requirements):
    init_key = f'{str(requirements.get("location_id") or "")}:{str(requirements.get("service_provider_id") or "")}:{str(requirements.get("container_size") or  "")}:{str(requirements.get("container_type") or "")}:{str(requirements.get("commodity") or "")}:{str(requirements.get("rate_type") or "")}'
    return init_key


def get_current_predicted_count(requirements):
    if rd:
        try:
            cached_response = rd.hget(
                current_processing_key, build_init_key(requirements)
            )
            return int(cached_response)
        except:
            return 0


def set_predicted_count(requirements, count):
    if rd:
        rd.hset(current_processing_key, build_init_key(requirements), int(count) + 1)


def delete_init_key(requirements):
    rd.hdel(current_processing_key, build_init_key(requirements))


def create_jobs_for_predicted_fcl_customs_rate(is_predicted, requirements):
    if is_predicted:
        current_count = get_current_predicted_count(requirements)
        if current_count >= 3:
            data = create_fcl_customs_rate_job(requirements, "spot_search")
            delete_init_key(requirements)
            return {"init_key": requirements}
        else:
            set_predicted_count(requirements, current_count)
            return {"init_key": requirements}
    else:
        current_count = get_current_predicted_count(requirements)
        if current_count:
            delete_init_key(requirements)
            return {"init_key": requirements}