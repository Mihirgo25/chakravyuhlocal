from database.db_session import rd

def get_key(service):
    return f"total_eligible_organizations{service}"

def get_eligible_organizations(service, relevant_ids):
    if relevant_ids:
        rd.hset(get_key(service), relevant_ids)
        rd.expire(get_key(service), 3600)
    else:
        cached_response = rd.hget(get_key(service))
    return cached_response
