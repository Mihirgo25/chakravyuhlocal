
from database.db_session import rd


def task_distribution_sysytem():
    users = {
        1: "user_id_1",
        2: "user_id_2",
        # ... up to 10
    }

    # Retrieve last_assigned_user from Redis
    # last_assigned_user = redis.get("last_assigned_user")
    # if not last_assigned_user:
    #     last_assigned_user = 1
    # else:
    #     last_assigned_user = int(last_assigned_user)

    # # Assign a job
    # assigned_user_id = users[last_assigned_user]

    # # Increment and wrap around using modulo
    # next_user = (last_assigned_user % len(users)) + 1

    # # Store the next user back to Redis
    # redis.set("last_assigned_user", next_user)
