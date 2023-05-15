from services.nandi.models.draft_fcl_freight_rate_local import DraftFclFreightRateLocal
from database.db_session import db
from fastapi import HTTPException

def update_draft_fcl_freight_rate_local_data(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    draft_freight_local = DraftFclFreightRateLocal.select().where(DraftFclFreightRateLocal.id == request["id"]).first()

    if not draft_freight_local:
        raise HTTPException(status_code=400, detail="rate does not exist")

    required_fields = ['data', 'source', 'status']

    for key in required_fields:
      if request.get(key):
          setattr(draft_freight_local, key, request[key])

    try:
       draft_freight_local.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail="rate did not update")

    return {'id': draft_freight_local.id}