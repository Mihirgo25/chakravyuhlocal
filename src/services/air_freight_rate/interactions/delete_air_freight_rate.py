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
        raise HTTPException(status_code=404,detail="Air Freight Rate Not Found")

    air_freight_rate.set_validities(  
        request.get("validity_start"),
        request.get("validity_end"),
        request.get("min_price"),
        request.get("currency"),
        request.get("weight_slabs"),
        True,
        None,
        request.get("density_category"),
        request.get("density_ratio"),
        request.get("initial_volume"),
        request.get("initial_gross_weight"),
        request.get("available_volume"),
        request.get("available_gross_weight"),
        request.get("rate_type"),
        request.get('likes_count'),
        request.get('dislikes_count')
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
    
    send_stats(request,air_freight_rate)

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
        object_type='AirFreghtRate',
        performed_by_type = request.get("performed_by_type") or "agent"
        )
    
def find_object(request):
    try:
        air_freight_rate=AirFreightRate.select().where(AirFreightRate.id==request.get('id')).first()
    except :
        air_freight_rate=None
    return air_freight_rate

def send_stats(request, freight):
    from services.bramhastra.celery import send_air_rate_stats_in_delay

    send_air_rate_stats_in_delay.apply_async(
        kwargs={"action": "delete", "request": request, "freight": freight},
        queue="statistics",
    )