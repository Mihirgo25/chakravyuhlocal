from services.nandi.models.draft_fcl_freight_rate_local import DraftFclFreightRateLocal
from services.nandi.models.draft_fcl_freight_rate_local_audit import DraftFclFreightRateLocalAudit
from database.db_session import db
from fastapi import HTTPException

def create_draft_fcl_freight_rate_local_data(request):
    with db.atomic():
        return create_draft_fcl_freight_rate_local(request)

def create_draft_fcl_freight_rate_local(request):
    row = {
        "commodity" : request.get("commodity"),
        "container_size" : request.get("container_size"),
        "container_type" : request.get("container_type"),
        "rate_id" : request.get("rate_id"),
        "data" : request.get("data"),
        "source" : request.get("source"),
        "status" : request.get("status"),
        "invoice_url" : request.get("invoice_url"),
        "invoice_date" : request.get("invoice_date"),
        "main_port_id" : request.get("main_port_id"),
        "port" : request.get("port"),
        "port_id" : request.get("port_id"),
        "shipping_line" : request.get("shipping_line"),
        "shipping_line_id" : request.get("shipping_line_id"),
        "trade_type" : request.get("trade_type"),
        "shipment_serial_id" : request.get("shipment_serial_id")
    }

    draft_freight_local = DraftFclFreightRateLocal(**row)
    draft_freight_local.set_main_port()

    try:
       draft_freight_local.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="draft fcl local did not save")

    create_audit(request, draft_freight_local.id)
    return {'id': draft_freight_local.id}

def create_audit(request, draft_fcl_local_id):

    try:
        DraftFclFreightRateLocalAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = request.get("data"),
        source = request.get("source"),
        object_id = draft_fcl_local_id,
        object_type = 'DraftFclFreightRateLocal'
      )
    except Exception as e:
      print('errr audit errr', e)
      raise HTTPException(status_code=500, detail='draft fcl freight local audit did not save')