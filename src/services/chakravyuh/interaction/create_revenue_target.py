from services.chakravyuh.models.revenue_target import RevenueTarget
from database.db_session import db
from fastapi.exceptions import HTTPException

def create_revenue_target(request):
    with db.atomic():
        return transaction(request)
    
def transaction(request):
    target = RevenueTarget.select().where(
        RevenueTarget.service_type == request.get('service_type'),
        RevenueTarget.origin_location_id == request.get('origin_location_id'),
        RevenueTarget.destination_location_id == request.get('destination_location_id'),
        RevenueTarget.date == request.get('date')
    ).first()
    
    if not target:
        target = RevenueTarget(**create_params(request))
    else:
        target.total_loss += request.get('total_loss')
        target.total_revenue += request.get('total_revenue')
        target.total_volume += request.get('total_volume')
        
    try:
        target.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    target.create_audit(audit_params(request, target))
    
    return {
        "id": target.id
    }
    
def create_params(request):
    params = { k: v for k, v in request.items() if k not in ['performed_by_id', 'performed_by_type']}
    return params

def audit_params(request, target):
    data = {
        "total_loss": target.total_loss,
        "total_revenue": target.total_revenue,
        "total_volume": target.total_volume,
        "total_currency": target.total_currency
    }
    
    param = {
        "source": "Revenue Desk",
        "object_id": target.id,
        "action_name": "create",
        "data": data,
        "performed_by_id": request.get('performed_by_id')
    }
    return param