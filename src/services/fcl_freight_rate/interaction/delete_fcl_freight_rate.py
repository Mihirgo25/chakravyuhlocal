from services.fcl_freight_rate.models.fcl_freight_rate import *
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from fastapi import HTTPException
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_platform_prices import update_fcl_freight_rate_platform_prices

def delete_fcl_freight_rate(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    object = find_object(request)

    if not object:
        raise HTTPException(status_code=404, detail="Rate id not found")

    object.set_validities(request['validity_start'].date(),request['validity_end'].date(),[],None,True,request['payment_term'])
    object.set_platform_prices()
    object.set_is_best_price()
    object.set_last_rate_available_date()
    try:
        object.save()
    except Exception as e:
        print("Exception in saving freight rate", e)

    object.create_trade_requirement_rate_mapping(request["procured_by_id"], request["performed_by_id"])

    create_audit(request, object.id)

    update_platform_prices_for_other_service_providers(object)

    return {
      'id': object.id
    }

def create_audit(request, freight_id):

    audit_data = {}
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()

    FclFreightRateAudit.create(
        bulk_operation_id = request.get('bulk_operation_id'),
        action_name = 'delete',
        performed_by_id = request['performed_by_id'],
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

def update_platform_prices_for_other_service_providers(object):
    update_fcl_freight_rate_platform_prices({
    'origin_port_id' : object.origin_port_id, 
    'origin_main_port_id' : object.origin_main_port_id, 
    'destination_port_id' : object.destination_port_id, 
    'destination_main_port_id' : object.destination_main_port_id, 
    'container_size' : object.container_size, 
    'container_type' : object.container_type, 
    'commodity' : object.commodity, 
    'shipping_line_id' : object.shipping_line_id, 
    'importer_exporter_id' : object.importer_exporter_id})
