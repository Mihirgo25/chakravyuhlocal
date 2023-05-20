from services.nandi.models.draft_fcl_freight_rate import DraftFclFreightRate
from database.db_session import db
from fastapi import HTTPException

def update_draft_fcl_freight_rate_data(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    draft_freight = DraftFclFreightRate.select().where(DraftFclFreightRate.id == request["id"]).first()

    if not draft_freight:
        raise HTTPException(status_code=400, detail="rate does not exist")

    required_fields = ['rate_id', 'data', 'source', 'status', 'invoice_url', 'invoice_date']

    for key in required_fields:
      if request[key]:
          setattr(draft_freight, key, request[key])

    try:
       draft_freight.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail="rate did not update")

    return {'id': draft_freight.id}