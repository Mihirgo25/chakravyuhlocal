
from database.db_session import rd
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_COVERAGE_USERS
from configs.fcl_freight_rate_constants import FCL_COVERAGE_USERS


def task_distribution_system(service_type):
    if service_type.upper()== 'FCL':
        users = FCL_COVERAGE_USERS
        redis_key = 'last_assigned_user_fcl'
    elif service_type.upper()== 'AIR':
        users = AIR_COVERAGE_USERS
        redis_key = 'last_assigned_user_air'

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
