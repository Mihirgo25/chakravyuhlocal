from redlock import Redlock


redis_host ={'host': 'localhost', 'port': 6379, 'db': 0}

redis_lock = Redlock([redis_host])
