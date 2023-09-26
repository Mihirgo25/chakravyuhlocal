from database.db_session import rd
from services.air_freight_rate.constants.air_freight_rate_constants import (
    AIR_COVERAGE_USERS,
)
from configs.fcl_freight_rate_constants import (
    FCL_COVERAGE_USERS,
    FCL_LOCAL_COVERAGE_USERS,
)
from configs.haulage_freight_rate_constants import HAULAGE_COVERAGE_USERS
from configs.fcl_customs_rate_constants import FCL_CUSTOMS_COVERAGE_USERS


def allocate_jobs(service_type: str) -> str:
    """
    Allocate jobs to users based on round robin method
    based on the service expertise of the user
    :param service_type: The type of service ('FCL' or 'AIR')
    :type service_type: str
    :return: The allocated user
    :rtype: str
    """
    if service_type.upper() == "FCL":
        users = FCL_COVERAGE_USERS
        redis_key = "last_assigned_user_fcl"
    elif service_type.upper() == "AIR":
        users = AIR_COVERAGE_USERS
        redis_key = "last_assigned_user_air"
    elif service_type.upper() == "HAULAGE":
        users = HAULAGE_COVERAGE_USERS
        redis_key = "last_assigned_user_haulage"
    elif service_type.upper() == "FCL_CUSTOMS":
        users = FCL_CUSTOMS_COVERAGE_USERS
        redis_key = "last_assigned_user_fcl_customs"
    elif service_type.upper() == "FCL_LOCALS":
        users = FCL_LOCAL_COVERAGE_USERS
        redis_key = "last_assigned_user_fcl_locals"

    last_assigned_user = rd.get(redis_key)
    if not last_assigned_user:
        last_assigned_user = 1
    else:
        last_assigned_user = int(last_assigned_user)

    # Increment and wrap around using modulo
    next_user = (last_assigned_user % len(users)) + 1

    # Store the next user back to Redis
    rd.set(redis_key, next_user)
    return users[next_user]
