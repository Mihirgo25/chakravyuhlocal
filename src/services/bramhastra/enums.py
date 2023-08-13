from enum import Enum


class Bramhastra(Enum):
    pass


class Table(Bramhastra):
    fcl_freight_rate_statistics = "fcl_freight_rate_statistics"
    feedback_fcl_freight_rate_statistics = "feedback_fcl_freight_rate_statistics"
    air_freight_rate_statistics = "air_freight_rate_statistics"
    feedback_air_freight_rate_statistics = "feedback_air_freight_rate_statistics"


class ValidityAction(Bramhastra):
    create = "create"
    update = "update"
    unchanged = "unchanged"


class FeedbackAction(Bramhastra):
    create = "create"
    update = "update"
    delete = "delete"


class CheckoutAction(Bramhastra):
    create = "create"
    update = "update"


class RequestAction(Bramhastra):
    create = "create"
    update = "update"
    delete = "delete"


class ShipmentAction(Bramhastra):
    create = "create"
    update = "update"
    delete = "delete"
    

class RDAction(Bramhastra):
    create = "create"
    update = "update"


class RedisKeys(Bramhastra):
    fcl_freight_rate_all_time_accuracy_chart = (
        "fcl_freight_rate_all_time_accuracy_chart"
    )


class DTString(Bramhastra):
    rate_monitoring = "rate_montioring"


class ShipmentServices(Bramhastra):
    fcl_freight_service = 'fcl_freight_service'
    
class ShipmentState(Bramhastra):
    confirmed_by_importer_exporter = 'confirmed_by_importer_exporter'
    
class FclModes(Bramhastra):
    rate_extension = 'rate_extension'
    manual = 'manual'
    rate_sheet = 'rate_sheet'
    predicted = 'predicted'
    cluster_extension = 'cluster_extension'
    disliked_rate = 'disliked_rate'
    flash_booking = 'flash_booking'
    rms_upload = 'rms_upload'
    missing_rate = 'missing_rate'
    spot_negotation = 'spot_negotation'
    
class FclParentMode(Bramhastra):
    supply = 'supply'
    rate_extension = 'rate_extension'
    predicted = 'predicted'
    cluster_extension = 'cluster_extension'