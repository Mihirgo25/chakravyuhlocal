from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from database.db_session import db

def update_fcl_customs_rate_platform_prices(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    query_result = FclCustomsRate.select().where(
        FclCustomsRate.location_id == request.get('location_id'),
        FclCustomsRate.trade_type == request.get('trade_type'),
        FclCustomsRate.container_size == request.get('container_size'),
        FclCustomsRate.container_type == request.get('container_type'),
        ((FclCustomsRate.commodity == request.get('commodity')) | (FclCustomsRate.commodity.is_null(True))),
        ((FclCustomsRate.importer_exporter_id == request.get('importer_exporter_id')) | (FclCustomsRate.importer_exporter_id.is_null(True))),
        FclCustomsRate.is_customs_line_items_error_messages_present == request.get('is_customs_line_items_error_messages_present'),
        FclCustomsRate.is_cfs_line_items_error_messages_present == request.get('is_cfs_line_items_error_messages_present'),
        FclCustomsRate.rate_type == DEFAULT_RATE_TYPE,
        ((FclCustomsRate.cargo_handling_type == request.get('cargo_handling_type')) | (FclCustomsRate.cargo_handling_type.is_null(True)))
    ).execute()

    for result in query_result:
        result.set_platform_price()
        result.set_is_best_price()
        result.save()