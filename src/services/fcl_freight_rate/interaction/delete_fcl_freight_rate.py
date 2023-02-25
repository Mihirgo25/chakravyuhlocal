from services.fcl_freight_rate.models.fcl_freight_rates import *
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from fastapi import HTTPException
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_platform_prices import update_fcl_freight_rate_platform_prices

def delete_fcl_freight_rate(request):
    object = find_object(request)

    if not object:
        raise HTTPException(status_code=499, detail="Rate id not found")
        # self.errors.add('{} is invalid'.format(request['id']))

    object.set_validities(request['validity_start'].date(),request['validity_end'].date(),[],None,True,request['payment_term'])
    # object.set_platform_prices()
    # object.set_is_best_price()
    # object.set_last_rate_available_date()
    try:
        object.save()
    except Exception as e:
        print("Exception in saving freight rate", e)
    # if not object.save():
    #     raise HTTPException(status_code=499, detail="Rate did not save")

    # object.create_trade_requirement_rate_mapping(request["procured_by_id"], request["performed_by_id"])

    create_audit(request, object.id)

    # update_platform_prices_for_other_service_providers(object)

    return {
      id: object.id
    }

def create_audit(request, freight_id):

    audit_data = {}
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()

    FclFreightRateAudit.create(
        bulk_operation_id = request.get('bulk_operation_id'),
        action_name = 'delete',
        performed_by_id = request['performed_by_id'],
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data,
        object_id = freight_id,
        object_type = 'FclFreightRate'
    )

def find_object(request):
    try:
        object = FclFreightRate.get_by_id(request['id'])
    except:
        object = None
    return object

def update_platform_prices_for_other_service_providers(self):
    self.update_fcl_freight_rate_platform_prices(self.origin_port_id, self.origin_main_port_id, self.destination_port_id, self.destination_main_port_id, self.container_size, self.container_type, self.commodity, self.shipping_line_id, self.importer_exporter_id)
