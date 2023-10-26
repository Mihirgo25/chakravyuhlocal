from enum import Enum


class Bramhastra(Enum):
    pass


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


class ShipmentServices(Bramhastra):
    fcl_freight_service = "fcl_freight_service"


class ShipmentState(Bramhastra):
    confirmed_by_importer_exporter = "confirmed_by_importer_exporter"
    shipment_received = "shipment_received"


class FclModes(Bramhastra):
    rate_extension = "rate_extension"
    manual = "manual"
    rate_sheet = "rate_sheet"
    predicted = "predicted"
    cluster_extension = "cluster_extension"
    disliked_rate = "disliked_rate"
    flash_booking = "flash_booking"
    rms_upload = "rms_upload"
    missing_rate = "missing_rate"
    spot_negotation = "spot_negotation"
    cogolens = "cogolens"


class FclParentMode(Bramhastra):
    supply = "supply"
    rate_extension = "rate_extension"
    predicted = "predicted"
    cluster_extension = "cluster_extension"


class Fcl(Bramhastra):
    default_currency = "USD"


class Air(Bramhastra):
    default_currency = "USD"


class ImportTypes(Bramhastra):
    parquet = "parquet"
    csv = "csv"
    postgres = "postgres"


class AppEnv(Bramhastra):
    production = "production"
    development = "development"
    
    
class EnvironmentType(Bramhastra):
    cli = "cli"
    app = "app"


class BrahmastraTrackStatus(Bramhastra):
    started = "started"
    failed = "failed"
    completed = "completed"
    empty = "empty"


class BrahmastraTrackModuleTypes(Bramhastra):
    table = "table"
    function = "function"


class AirSources(Bramhastra):
    manual = "manual"
    predicted = "predicted"
    rate_extension = "rate_extension"
    rate_sheet = "rate_sheet"
    freight_look = "freight_look"
    cargo_ai = "cargo_ai"


class FclFeedbackClosingRemarks(Bramhastra):
    rate_added = "rate_added"


class FclFeedbackStatus(Bramhastra):
    active = "active"
    inactive = "inactive"


class FclFilterTypes(Bramhastra):
    validity_range = "validity_range"
    time_series = "time_series"


class FclChargeCodes(Bramhastra):
    BAS = "BAS"


class MapsFilter(Bramhastra):
    origin_port_code = "origin_port_code"
    destination_port_code = "destination_port_code"


class Status(Bramhastra):
    active = "active"
    inactive = "inactive"


class FclDefault(Bramhastra):
    container_type = "standard"
    container_size = "20"
    commodity = "general"


class Paginate(Bramhastra):
    global_limit = 1000


class SelectTypes(Bramhastra):
    SO1 = "SO1"


class ShipmentState(Bramhastra):
    empty = 0
    shipment_received = 1
    confirmed_by_importer_exporter = 2
    in_progress = 3
    cancelled = 4
    aborted = 5
    completed = 6


class FeedbackType(Bramhastra):
    empty = 0
    disliked = 1
    liked = 2


class FeedbackState(Bramhastra):
    empty = 0
    created = 1
    closed = 2
    rate_added = 3


class RevenueDeskState(Bramhastra):
    empty = 0
    visited = 1
    selected_for_preference = 2
    selected_for_booking = 3


class ShipmentServiceState(Bramhastra):
    empty = 0
    init = 1
    containers_gated_out = 2
    containers_gated_in = 3
    cancelled = 4
    awaiting_service_provider_confirmation = 5
    confirmed_by_service_provider = 6
    vessel_arrived = 7
    vessel_departed = 8
    completed = 9
    aborted = 10


class RateRequestState(Bramhastra):
    empty = 0
    created = 1
    closed = 2
    rate_added = 3
