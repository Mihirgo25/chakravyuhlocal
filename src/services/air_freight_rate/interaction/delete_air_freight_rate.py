from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudits
from playhouse.postgres_ext import *
from database.db_session import db
def execute(request):
    db.atomic()
    return delete_air_freight_rate(request)

def delete_air_freight_rate(request):
    air_freight_rate=find_object(request)

    if not air_freight_rate:
        raise HTTPException(status_code=400,details="is invalid")
    
    validities=air_freight_rate['validities']
    matching_validity = next((t for t in validities if t['id'] == request.get('validity_id')), None)

    if matching_validity:
        matching_validity['status'] = False 
    total_avaliable_validities=len(validities)

    if total_avaliable_validities ==1:
        air_freight_rate['rate_not_avaliable_entry']=True
    
    validities=air_freight_rate['validities']
    matching_validity = next((t for t in validities if t['id'] == request.get('validity_id')), None)

    for validity in air_freight_rate['validities']:
        if validity.get("status",True):
            air_freight_rate['rate_not_avaliable_entry']=False
            break
    if air_freight_rate['rate_not_avaliable_entry']==False:
        air_freight_rate.set_last_rate_avaliable_rate()
    try:
        air_freight_rate.save()
    except Exception as e:
        print("Exception in saving freight rate", e)
    

    create_audit(request, air_freight_rate.id)

    return {
        id:air_freight_rate.id
    }


def create_audit(request,freight_id):
    audit_data={}
    audit_data["validity_id"]=request["validity_id"]

    AirFreightRateAudits.create(
        bulk_operation_id=request['bulk_operation_id'],
        action_name='delete',
        data=audit_data,
        performed_by_id=request['performed_by_id'],
        validity_id=request['validity_id'],
        object_id = freight_id,
        object_type='AirFreghtRate'
        )
    
def find_object(request):
    try:
        air_freight_rate=AirFreightRate.get_by_id(request['id'])
    except:
        air_freight_rate=None
    return air_freight_rate




    
        

    
    
