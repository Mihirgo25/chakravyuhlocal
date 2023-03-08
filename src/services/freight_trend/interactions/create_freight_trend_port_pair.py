
from services.freight_trend.models.freight_trend_port_pair import FreightTrendPortPair
from redis_lock import redis_lock
def create_freight_trend_port_pair(origin_port_id,destination_port_id):
    return lock_and_execute_transaction_code(origin_port_id,destination_port_id)  

def lock_and_execute_transaction_code(origin_port_id,destination_port_id):
    # lockinfo redis

    lock_info = redis_lock.lock(f"create_freight_trend_port_pair_{origin_port_id}_{destination_port_id}",200)
    
    if lock_info:
        return execute_transaction_code(origin_port_id,destination_port_id)
    
    return {}

def execute_transaction_code(origin_port_id,destination_port_id):
    port_pair = FreightTrendPortPair.where(FreightTrendPortPair.origin_port_id == origin_port_id,FreightTrendPortPair.destination_port_id == destination_port_id).first()

    if port_pair:
        return {'id':port_pair.id}
    
    port_pair = FreightTrendPortPair(origin_port_id = origin_port_id,destination_port_id= destination_port_id)
    
    if not port_pair.save():
        return 
    
    return {'id':port_pair.id}




