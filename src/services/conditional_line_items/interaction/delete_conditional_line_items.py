from services.conditional_line_items.models.conditional_line_items import ConditionalLineItems
from database.db_session import db

def create_conditional_line_items(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    condition_key = request.get('charge_code') + '_' + request.get('search_key')
    query = ConditionalLineItems.select(
        ConditionalLineItems.condition_key == condition_key
    )