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
    