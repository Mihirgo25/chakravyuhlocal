from services.chakravyuh.models.demand_transformation import DemandTransformation
from database.db_session import db
from fastapi.exceptions import HTTPException

def create_demand_transformation(request):
    with db.atomic():
        return transaction(request)
    
def transaction(request):
    demand = DemandTransformation.select().where(
        DemandTransformation.service_type == request.get('service_type'),
        DemandTransformation.origin_location_id == request.get('origin_location_id'),
        DemandTransformation.destination_location_id == request.get('destination_location_id'),
        DemandTransformation.date == request.get('date')
    ).first()
    
    if not demand:
        demand = DemandTransformation(**create_params(request))
    else:
        demand.net_profit += request.get('net_profit')
        demand.realised_revenue += request.get('realised_revenue')
        demand.realised_volume += request.get('realised_volume')
        
    try:
        demand.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    demand.create_audit(audit_params(request, demand))
    
    return {
        "id": demand.id
    }  

def create_params(request):
    params = { k: v for k, v in request.items() if k not in ['performed_by_id', 'performed_by_type']}
    return params

def audit_params(request, demand):
    data = {
        "net_profit": demand.net_profit,
        "realised_revenue": demand.realised_revenue,
        "realised_volume": demand.realised_volume,
        "realised_currency": demand.realised_currency
    }
    
    param = {
        "source": "Revenue Desk",
        "object_id": demand.id,
        "action_name": "create",
        "data": data,
        "performed_by_id": request.get('performed_by_id')
    }
    return param