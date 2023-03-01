from services.fcl_freight_rate.models.fcl_freight_rate_task import FclFreightRateTask
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit


def validate_closing_remarks(request):
    if request.get('closing_remarks') is not None and request.get('closing_remarks') not in ['Sid Cancelled/Changed','Port Currently not served']:
        raise HTTPException(status_code=400, detail="Closing remarks is not valid")
    
def update_fcl_freight_rate_data(request):
    validate_closing_remarks(request)
    freight_object = FclFreightRateTask.get_by_id(request['id'])
    freight_object.closing_remarks = request.get('closing_remarks')
    freight_object.save()
    return {
        'id': freight_object.id,
        'closing_remarks': freight_object.closing_remarks,
        'status': freight_object.status
    }