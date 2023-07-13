from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from playhouse.postgres_ext import *
from database.db_session import db

def delete_air_freight_rate(request):
    with db.atomic():
        return delete_air_freight_rate_data(request)

def delete_air_freight_rate_data(request):
    air_freight_rate=find_object(request)

    if not air_freight_rate:
        raise HTTPException(status_code=400,detail="is invalid")

    for t in air_freight_rate.validities:
        if t.get("id") == request.get("validity_id"):
            air_freight_rate.set_validities(
                None,
                None,
                t.get("min_price"),
                t.get('currency'),
                t.get("weight_slabs"),
                True,
                request.get("validity_id"),
                t.get("density_category"),
                t.get('density_ratio'),
                t.get('initial_volume'),
                t.get('initial_gross_weight'),
                t.get('available_volume'),
                t.get('available_gross_weight'),
                air_freight_rate.rate_type,
                t.get('likes_count'),
                t.get('dislikes_count')
            )

    validities =  air_freight_rate.validities
    total_avaliable_validities = len(validities)

    if total_avaliable_validities ==0:
        air_freight_rate.rate_not_available_entry=True

    if air_freight_rate.rate_not_available_entry==False:
        air_freight_rate.set_last_rate_available_date()

    air_freight_rate.validities = validities

    try:
        air_freight_rate.save()
    except Exception as e:
        print("Exception in saving freight rate", e)
    
    create_audit(request, air_freight_rate.id)

    return {
       'id': air_freight_rate.id
    }


def create_audit(request,freight_id):
    audit_data={}
    audit_data["validity_id"]=request["validity_id"]

    AirFreightRateAudit.create(
        bulk_operation_id=request.get('bulk_operation_id'),
        action_name='delete',
        data=audit_data,
        performed_by_id=request.get('performed_by_id'),
        validity_id=request.get('validity_id'),
        object_id = freight_id,
        object_type='AirFreghtRate'
        )
    
def find_object(request):
    try:
        air_freight_rate=AirFreightRate.select().where(AirFreightRate.id==request.get('id')).first()
    except :
        air_freight_rate=None
    return air_freight_rate