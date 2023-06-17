from services.nandi.models.draft_fcl_freight_rate import DraftFclFreightRate
from services.nandi.models.draft_fcl_freight_rate_audit import DraftFclFreightRateAudit
from database.db_session import db
from fastapi import HTTPException

def update_draft_fcl_freight_rate_data(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    draft_freight = DraftFclFreightRate.select().where(DraftFclFreightRate.id == request["id"]).first()

    if not draft_freight:
        raise HTTPException(status_code=400, detail="rate does not exist")

    required_fields = ['data', 'source', 'status']

    for key in required_fields:
      if request.get(key):
          setattr(draft_freight, key, request[key])

    try:
       draft_freight.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail="rate did not update")

    create_audit(request, draft_freight.id)
    return {'id': draft_freight.id}

def create_audit(request, draft_fcl_id):
    audit_data = {"status": request.get("status")}
    try:
        DraftFclFreightRateAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = audit_data,
        source = request.get("source"),
        object_id = draft_fcl_id,
        object_type = 'DraftFclFreightRate'
      )
    except:
      raise HTTPException(status_code=500, detail='draft fcl freight audit did not save')