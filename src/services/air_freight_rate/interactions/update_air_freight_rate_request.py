from fastapi import HTTPException
from datetime import datetime
from database.db_session import db 
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from uuid import UUID

def update_air_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):

    object=AirFreightRateRequest.select().where(AirFreightRateRequest.id==request.get('air_freight_rate_request_id')).first()
    if not object:
        raise HTTPException(status_code=404, detail="Invalid Rate Request")
    
    object.remarks = request.get('remarks')
    if request.get("closing_remarks"):
        if "rate_added" in request.get("closing_remarks"):
            object.reverted_rates_count = (
                object.reverted_rates_count + 1
                if object.reverted_rates_count is not None
                else 1
            )
            object.reverted_by_user_ids = (
                object.reverted_by_user_ids.append(UUID(request.get("performed_by_id")))
                if object.reverted_by_user_ids is not None
                else [UUID(request.get("performed_by_id"))]
            )
        object.closing_remarks = (
            object.closing_remarks.append(request.get("closing_remarks"))
            if object.closing_remarks is not None
            else [request.get("closing_remarks")]
        )
    object.validate()
    try :
        object.save()
        
    except:
        raise HTTPException(status_code=400, detail="error while saving the data")
    
    create_audit(request,request['air_freight_rate_request_id'])

    return {
        'id':str(request['air_freight_rate_request_id'])
    }
    
def create_audit(request,air_freight_rate_request_id):
        AirServiceAudit.create(
        action_name="update",
        performed_by_id=request["performed_by_id"],
        data={
            "closing_remarks": request.get("closing_remarks"),
            "performed_by_id": request.get("performed_by_id"),
        },
        object_id=air_freight_rate_request_id,
        object_type="AirFreightRateRequest",
    )


