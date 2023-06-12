from database.db_session import db
from services.air_freight_rate.models.air_freight_rate_request import AirFreightRateRequest
from datetime import *
from playhouse.postgres_ext import *
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudits
from celery_worker import update_multiple_service_objects
def create_air_freight_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):

    existing_missing_request = AirFreightRateRequest.update(status = 'inactive').where(
        AirFreightRateRequest.source == 'shipment',
        AirFreightRateRequest.source_id == request.get('source_id'),
        AirFreightRateRequest.status == 'active'
    )

    unique_object_params = {
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    request_object = AirFreightRateRequest.select().where(
        AirFreightRateRequest.source == request.get('source'),
        AirFreightRateRequest.source_id == request.get('source_id'),
        AirFreightRateRequest.performed_by_id == request.get('performed_by_id'),
        AirFreightRateRequest.performed_by_type == request.get('performed_by_type'),
        AirFreightRateRequest.performed_by_org_id == request.get('performed_by_org_id')
    ).first()

    if not request_object:
        request_object = AirFreightRateRequest(**unique_object_params)
    create_params = get_create_params(request)

    for attr, value in create_params.items():
        if attr =='preffered_airline_ids' and value:
            ids=[]
            for val in value:
                ids.append(uuid.UUID(str(val)))
            setattr(request_object,attr,ids)
        else:
            setattr(request_object, attr, value)
    
    if request_object.validate():
        request_object.save()


    create_audit(request, request_object.id)

    # for air 
    update_multiple_service_objects.apply_async(kwargs={'object':request_object},queue='low')

    
    # send_notifications_to_supply_agents(request)

    return {
    'id': str(request_object.id)
    }

def get_create_params(request):
    return {key:value for key,value in request.items() if key not in ['source', 'source_id', 'performed_by_id', 'performed_by_type', 'performed_by_org_id']} | ({'status': 'active'})


def create_audit(request, request_object_id):
    performed_by_id = request.get('performed_by_id')
    del request['performed_by_id']
    if request.get('cargo_readiness_date'):
        request['cargo_readiness_date'] = request.get('cargo_readiness_date').isoformat()

# change to air service audits
    AirFreightRateAudits.create(
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_type = 'AirFreightRateRequest',
        object_id = request_object_id
    )