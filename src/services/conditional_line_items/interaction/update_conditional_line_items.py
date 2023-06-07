from services.conditional_line_items.models.conditional_line_items import ConditionalLineItems
from database.db_session import db
from fastapi import HTTPException

def update_conditional_line_items(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    
