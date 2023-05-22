from services.nandi.models.draft_fcl_freight_rate import DraftFclFreightRate
from database.db_session import db
from fastapi import HTTPException

def create_draft_fcl_freight_rate_data(request):
    with db.atomic():
        return create_draft_fcl_freight_rate(request)

def create_draft_fcl_freight_rate(request):
    row = {
        "rate_id" : request.get("rate_id"),
        "data" : request.get("data"),
        "source" : request.get("source"),
        "status" : request.get("status"),
        "invoice_url" : request.get("invoice_url"),
        "invoice_date" : request.get("invoice_date"),
        "shipment_serial_id" : request.get("shipment_serial_id")
    }

    draft_freight = DraftFclFreightRate(**row)

    try:
       draft_freight.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="rate did not save")

    return {'id': draft_freight.id}