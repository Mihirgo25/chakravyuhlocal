from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit

def get_air_freight_rate_audit(request):

    object=AirFreightRate.select(
        AirFreightRate.procured_by,
        AirFreightRate.procured_by_id,
        AirFreightRate.sourced_by,
        AirFreightRate.sourced_by_id,
        AirFreightRate.updated_at
    ).where(AirFreightRate.id==request['id']).first()

    # audit=AirFreightRateAudit.select(AirFreightRateAudit.performed_by_id).where(AirFreightRateAudit.object_id==request['id'],AirFreightRateAudit.action_name=='create').order_by(AirFreightRateAudit.updated_at.desc()).first()
    if object :
        return{
            "procured_by":object.procured_by,
            "procured_by_id":object.procured_by_id,
            "sourced_by":object.sourced_by,
            "sourced_by_id":object.sourced_by_id,
            "updated_at":object.updated_at,
            # "performed_by_id":audit.performed_by_id,
            # "performed_by":""
        }
    else:
        return {}