from services.fcl_freight_rate.models.fcl_freight_rate_commodity_surcharge import FclFreightRateCommoditySurcharge
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from database.db_session import db
from fastapi import HTTPException


def create_fcl_freight_rate_commodity_surcharge(request):
    with db.atomic() as transaction:
        try:
          return execute_transaction_code(request)
        except:
            transaction.rollback()
            return "Creation Failed"

def execute_transaction_code(request):
    commodity_surcharge = get_commodity_surcharge_object(request)

    try:
        commodity_surcharge.save()
    except:
        raise HTTPException(status_code=499, detail="commodity surcharge failed to create")
#       self.errors.merge!(commodity_surcharge.errors)


    commodity_surcharge.update_freight_objects()
    commodity_surcharge.save()

    create_audit(request, commodity_surcharge.id)

    return {
      'id': commodity_surcharge.id
    }
#   end

def get_commodity_surcharge_object(request):
    commodity_surcharge = FclFreightRateCommoditySurcharge.get(
        origin_location_id = request['origin_location_id'],
        destination_location_id = request['destination_location_id'],
        container_size = request['container_size'],
        container_type = request['container_type'],
        commodity = request['commodity'],
        shipping_line_id = request['shipping_line_id'],
        service_provider_id = request['service_provider_id']
    )
    ############## check this
    for key in ['price', 'currency', 'remarks']:
        setattr(commodity_surcharge, key, request.get(key))

    return commodity_surcharge


def create_audit(request, commodity_surcharge_id):

    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        rate_sheet_id = request.get('rate_sheet_id'),
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = {'price': request['price'], 'currency': request['currency'], 'remarks': request.get('remarks')},
        object_id = commodity_surcharge_id,
        object_type = 'FclFreightRateCommoditySurcharge'
    )
