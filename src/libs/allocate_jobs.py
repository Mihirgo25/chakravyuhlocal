from database.db_session import rd
from services.air_freight_rate.constants.air_freight_rate_constants import (
    AIR_COVERAGE_USERS,
)
from configs.fcl_freight_rate_constants import (
    FCL_COVERAGE_USERS,
    FCL_LOCAL_COVERAGE_USERS,
)
from configs.haulage_freight_rate_constants import HAULAGE_FREIGHT_COVERAGE_USERS
from configs.fcl_customs_rate_constants import FCL_CUSTOMS_COVERAGE_USERS
from services.air_customs_rate.air_customs_rate_constants import (
    AIR_CUSTOMS_COVERAGE_USERS,
)
from services.ltl_freight_rate.ltl_freight_rate_constants import LTL_LOCAL_COVERAGE_USERS
from configs.ftl_freight_rate_constants import FTL_FREIGHT_COVERAGE_USERS
from configs.fcl_cfs_rate_constants import FCL_CFS_COVERAGE_USERS
from configs.lcl_customs_rate_constants import LCL_CUSTOMS_COVERAGE_USERS
from configs.lcl_freight_rate_constants import LCL_FREIGHT_COVERAGE_USERS
from micro_services.client import common



def allocate_jobs(service_type: str) -> str:
    """
    Allocate jobs to users based on round robin method
    based on the service expertise of the user
    :param service_type: The type of service ('FCL' or 'AIR')
    :type service_type: str
    :return: The allocated user
    :rtype: str
    """
    service_type = service_type.upper()
    if service_type in ["FCL", "AIR", "HAULAGE", "FCL_CUSTOMS", "AIR_CUSTOMS", "LCL_CUSTOMS",
                        "FCL_LOCALS", "AIR_LOCALS", "LTL", "FTL", "FCL_CFS", "LCL"]:
        users = globals()[f"{service_type}_COVERAGE_USERS"]
        redis_key = f"last_assigned_user_{service_type.lower()}"
    else:
        users = None
        redis_key = None
    

    last_assigned_user = rd.get(redis_key)
    if not last_assigned_user:
        last_assigned_user = 0
    else:
        last_assigned_user = int(last_assigned_user)

    # Increment and wrap around using modulo
    next_user = (last_assigned_user + 1) % len(users)

    # Store the next user back to Redis

    # Get the user ID for the next user to be assigned
    next_user_id = users[next_user]
    agent_filters = {}
    filters = {"agent_id": users}
    agent_filters['filters'] = filters
    online_users = common.list_chat_agents(agent_filters)
    if online_users:
        online_users = online_users['list']
    else:
        rd.set(redis_key, next_user)
        return users[next_user]

    user_activity = []
    for user in online_users:
        if user['status'] == 'active':
            user_activity.append(user['agent_id'])
    # Check if the next user is online and active
    if next_user_id in user_activity:
        # Set the allocated user in Redis
        rd.set(redis_key, next_user)
        return next_user_id
    else:
        # Find the next available online user in a round-robin manner
        for _ in range(len(users)):
            next_user = (next_user + 1) % len(users)
            next_user_id = users[next_user]
            if next_user_id in user_activity:
                # Set the allocated user in Redis
                rd.set(redis_key, next_user)
                return next_user_id
    
    # If no online users are available, return a message
    return "No online users available for job allocation."
