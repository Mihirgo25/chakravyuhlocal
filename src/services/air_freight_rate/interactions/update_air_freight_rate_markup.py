from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from fastapi import FastAPI, HTTPException
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from database.db_session import db
from datetime import datetime,timedelta

def create_audit(request):
    audit_data = {
        "validity_id": request.get("validity_id"),
        "validity_start": str(request.get("validity_start")),
        "validity_end": str(request.get("validity_end")),
    }
    AirFreightRateAudit.create(
        action_name="edit",
        performed_by_id=request.get("performed_by_id"),
        bulk_operation_id=request.get("bulk_operation_id"),
        data=audit_data,
        validity_id=request.get("validity_id"),
    )


def update_air_freight_rate_markup(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    object = AirFreightRate.select().where(AirFreightRate.id == request["id"]).first()
    if not object:
        raise HTTPException(status_code=400, detail=" Rate not found")
    validity_object = None

    for t in object.validities:
        if datetime.strptime(t['validity_end'],'%Y-%m-%d') < datetime.strptime(request['validity_end'],'%Y-%m-%d'):
            validity_object = t
        
    validity_start = max(datetime.strptime(validity_object['validity_start'], '%Y-%m-%d'), datetime.now())
    validity_end = min(datetime.strptime(request['validity_end'], '%Y-%m-%d'), (datetime.now() + timedelta(days=45)))
    object.set_validities(
        validity_start,
        validity_end,
        validity_object.get("min_price"),
        validity_object.get('currency'),
        validity_object.get("weight_slabs"),
        False,
        None,
        validity_object.get("density_category"),
        "1:{}".format(validity_object.get('min_density_weight')),
        validity_object.get('initial_volume'),
        validity_object.get('initial_gross_weight'),
        validity_object.get('available_volume'),
        t.get('available_gross_weight'),
        object.rate_type,
        validity_object.get('likes_count'),
        validity_object.get('dislikes_count')
    )
    object.set_last_rate_available_date

    try:
        object.save()
    except Exception:
        raise HTTPException(status_code=500, detail="MarkUp not updated")

    create_audit(request)

    return {"id": str(object.id)}