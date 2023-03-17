from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_seasonal_surcharge import create_fcl_freight_rate_seasonal_surcharge
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from database.db_session import db

def create_audit(request, fcl_freight_rate_seasonal_surcharge_id):
    audit_data = {}
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()
    audit_data['price'] = request['price']
    audit_data['currency'] = request['currency']
    audit_data['remarks'] = request.get('remarks')

    FclFreightRateAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data,
    )

def update_fcl_freight_rate_seasonal_surcharge(request):
    with db.atomic as transaction:
        try:
            execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            raise e

def execute_transaction_code(request):
    fcl_freight_rate_seasonal_surcharge = FclFreightRateSeasonalSurcharge.get(id=request['id'])

    if not fcl_freight_rate_seasonal_surcharge:
        raise HTTPException(status_code=404, detail="Seasonal Surcharge not found")
    
    for k, v in request.items():
        if k in ['price', 'currency', 'validity_start', 'validity_end', 'remarks']:
            setattr(fcl_freight_rate_seasonal_surcharge, k, v)

    if not fcl_freight_rate_seasonal_surcharge.save():
        raise HTTPException(status_code=422, detail="Seasonal Surcharge not updated")

    create_audit(request, fcl_freight_rate_seasonal_surcharge.id)