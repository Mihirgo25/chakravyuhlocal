from services.fcl_freight_rate.models.fcl_freight_rate_seasonal_surcharge import FclFreightRateSeasonalSurcharge
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from database.db_session import db
from fastapi import HTTPException


def create_fcl_freight_rate_seasonal_surcharge(request):
    with db.atomic() as transaction:
        try:
          return execute_transaction_code(request)
        except:
            transaction.rollback()
            return "Creation Failed"

def execute_transaction_code(request):
    seasonal_surcharge = get_seasonal_surcharge_object(request)

    try:
        seasonal_surcharge.save()
    except:
        raise HTTPException(status_code=499, detail="seasonal surcharge failed to create")
#       self.errors.merge!(commodity_surcharge.errors)


    seasonal_surcharge.update_freight_objects()
    seasonal_surcharge.save()

    create_audit(request, seasonal_surcharge.id)

    return {
      'id': seasonal_surcharge.id
    }
#   end

def get_seasonal_surcharge_object(request):
    seasonal_surcharge = FclFreightRateSeasonalSurcharge.get(
        origin_location_id = request['origin_location_id'],
        destination_location_id = request['destination_location_id'],
        container_size = request['container_size'],
        container_type = request['container_type'],
        shipping_line_id = request['shipping_line_id'],
        service_provider_id = request['service_provider_id'],
        code = request['code']
    )
    ############## check this
    for key in ['price', 'currency','validity_start', 'validity_end', 'remarks']:
        setattr(seasonal_surcharge, key, request.get(key))

    return seasonal_surcharge


def create_audit(request, seasonal_surcharge_id):

    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        rate_sheet_id = request.get('rate_sheet_id'),
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = {'price': request['price'], 'currency': request['currency'], 'remarks': request.get('remarks'), 'validity_start': request['validity_start'],'validity_end' :request['validity_end']},
        object_id = seasonal_surcharge_id,
        object_type = 'FclFreightRateSeasonalSurcharge'
    )
