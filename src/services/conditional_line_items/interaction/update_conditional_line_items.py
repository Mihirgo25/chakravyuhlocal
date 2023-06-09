from services.conditional_line_items.models.conditional_line_items import ConditionalLineItems
from services.conditional_line_items.models.conditional_line_items_audit import ConditionalLineItemAudit
from database.db_session import db
from fastapi import HTTPException

def update_conditional_line_items(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    object = find_object(request)

    if not object:
        raise HTTPException(status_code=400, detail="condition id not found")
    
    if request.get('charge_codce'):
        object.charge_code=request['charge_code']
    
    if request.get('data'):
        object.data=request['data']
        
    try:
        object.save()
    except:
        raise HTTPException(
            status_code=500, detail="conditions line_items  updation failed"
        )

    create_audit(request, object.id)
    
    return {
    'id': object.id
    }

def find_object(request):
    try:
        return (
            ConditionalLineItems.select()
            .where(ConditionalLineItems.id == request["id"]).first()
        )
    except:
        return None


def create_audit(request, id):
    ConditionalLineItemAudit.create(
        action_name="update",
        performed_by_id=request["performed_by_id"],
        data={
            "performed_by_id": request["performed_by_id"],
        },
        object_id=id,
        object_type="ConditionalLineItems",
    )

