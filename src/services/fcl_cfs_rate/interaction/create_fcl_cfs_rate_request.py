from peewee import *
from services.fcl_cfs_rate.models.fcl_cfs_rate_request import FclCfsRateRequest

def get_unique_object_params(request):
    return {
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

def get_create_params(request):
    return {
        'preferred_rate': request.get('preferred_rate'),
        'preferred_rate_currency': request.get('preferred_rate_currency'),
        'preferred_detention_free_days': request.get('preferred_detention_free_days'),
        'cargo_readiness_date': request.get('cargo_readiness_date'),
        'remarks': request.get('remarks'),
        'booking_params': request.get('booking_params'),
        'container_size': request.get('container_size'),
        'commodity': request.get('commodity'),
        'country_id': request.get('country_id'),
        'port_id': request.get('port_id'),
        'trade_type': request.get('trade_type'),
        'status': 'active'
    }

def create_audit(request):
    audit_params = {
        'action_name': 'create',
        'performed_by_id': request.get('performed_by_id'),
        'data': get_audit_params(request)
    }
    request.audits.create(**audit_params)

def get_audit_params(request):
    return {k: v for k, v in request.items() if k != 'performed_by_id'}


def create_fcl_cfs_rate_request(request):
    freight = FclCfsRateRequest.get_or_create(**get_unique_object_params(request))
    freight.set_attributes(get_create_params(request))

    if not freight.save():
        request.errors = freight.errors
        return

    create_audit(request)
    FclCfsRateRequest.send_notifications_to_supply_agents()

    return {'id': freight.id}

