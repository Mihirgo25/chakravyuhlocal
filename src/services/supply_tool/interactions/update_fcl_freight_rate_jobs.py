from database.db_session import db
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate
from services.supply_tool.models.fcl_freight_rate_jobs import FclFreightRateJobs
from datetime import datetime
from fastapi import HTTPException

def update_fcl_freight_rate_jobs(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    if type(request) != dict:
        request = request.dict(exclude_none = False)

    if request['key'] == 'add':
        pass # ADD FCL FREIGHT RATE

        update_params = {'status':'inactive'}
        update_params['updated_at'] = datetime.now()
        fcl_freight_rate_job = FclFreightRateJobs.update(update_params).where(FclFreightRateJobs.id == request['id'])

        if fcl_freight_rate_job.execute() == 0:
            raise HTTPException(status_code=500, detail="FCL Freight Rate Jobs not updated")

        return {'id' : request['id']}

    if request['key'] == 'close':
        update_params = {'status':'inactive'}
        update_params['updated_at'] = datetime.now()
        fcl_freight_rate_job = FclFreightRateJobs.update(update_params).where(FclFreightRateJobs.id == request['id'])

        if fcl_freight_rate_job.execute() == 0:
            raise HTTPException(status_code=500, detail="FCL Freight Rate Jobs not updated")

        return {'id' : request['id']}

