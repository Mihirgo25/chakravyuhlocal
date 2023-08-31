
from database.db_session import rd
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_COVERAGE_USERS
from configs.fcl_freight_rate_constants import FCL_COVERAGE_USERS


def task_distribution_sysytem(service_type):

    # Retrieve last_assigned_user from Redis
    last_assigned_user = rd.get("last_assigned_user")
    if not last_assigned_user:
        last_assigned_user = 1
    else:
        last_assigned_user = int(last_assigned_user)

    # Assign a job
    users = f"{service_type.upper()}_COVERAGE_USERS"

    # Increment and wrap around using modulo
    next_user = (last_assigned_user % len(users)) + 1

    # Store the next user back to Redis
    rd.set("last_assigned_user", next_user)
