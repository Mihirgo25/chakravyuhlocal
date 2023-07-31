from enum import Enum

class Bramhastra(Enum):
    pass


class Table(Bramhastra):
    fcl_freight_rate_statistics = 'fcl_freight_rate_statistics'
    feedback_fcl_freight_rate_statistics = 'feedback_fcl_freight_rate_statistics'
    air_freight_rate_statistics = 'air_freight_rate_statistics'
    
    
class ValidityAction(Bramhastra):
    create = 'create'
    update = 'update'
    unchanged = 'unchanged'
    
class FeedbackAction(Bramhastra):
    create = 'create'
    update = 'update'
    
    
class RedisKeys(Bramhastra):
    fcl_freight_rate_all_time_accuracy_chart = 'fcl_freight_rate_all_time_accuracy_chart'

class DTString(Bramhastra):
    rate_monitoring = 'rate_montioring'
    