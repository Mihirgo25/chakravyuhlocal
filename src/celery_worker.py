from celery import Celery
import os
from configs.env import *
from micro_services.client import organization, common
from datetime import datetime
from database.db_session import db_cogo_lens
from currency_converter import CurrencyConverter
from services.fcl_freight_rate.models.fcl_rate_prediction_feedback import FclRatePredictionFeedback
from services.fcl_freight_rate.interaction.send_fcl_freight_rate_task_notification import send_fcl_freight_rate_task_notification
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from celery.schedules import crontab

CELERY_CONFIG = {
    "enable_utc": True,
    "task_serializer": "pickle",
    "event_serializer": "pickle",
    "result_serializer": "json",
    "accept_content": ['application/json', 'application/x-python-serialize']
}
celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")
celery.conf.update(**CELERY_CONFIG)


@celery.task()
def create_fcl_freight_rate_delay(request):
    from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate
    return create_fcl_freight_rate(request)

@celery.task(max_retries=10)
def delay_fcl_functions(fcl_object,request):
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
    from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
    from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_request import delete_fcl_freight_rate_request
    print(create_freight_trend_port_pair(request))
    create_sailing_schedule_port_pair(request)
    if not FclFreightRate.select().where(FclFreightRate.service_provider_id==request["service_provider_id"], FclFreightRate.rate_not_available_entry==False).exists():
        organization.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})

    if request.get("fcl_freight_rate_request_id"):
        delete_fcl_freight_rate_request(request)
    
    # fcl_object.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])

    
    get_multiple_service_objects(fcl_object)



@celery.task()
def create_sailing_schedule_port_pair(request):
    port_pair_coverage_data = {
    'origin_port_id': request["origin_main_port_id"] if request.get("origin_main_port_id") else request["origin_port_id"],
    'destination_port_id': request["destination_main_port_id"] if request.get("destination_main_port_id") else request["destination_port_id"],
    'shipping_line_id': request["shipping_line_id"]
    }
    common.create_sailing_schedule_port_pair_coverage(port_pair_coverage_data)

def create_freight_trend_port_pair(request):
    port_pair_data = {
        'origin_port_id': request["origin_port_id"],
        'destination_port_id': request["destination_port_id"]
    }

  
  # common.create_freight_trend_port_pair(port_pair_data) expose

@celery.task()
def fcl_freight_local_data_updation(local_object,request):

    update_multiple_service_objects.apply_async(kwargs={"object":local_object},queue='low')

    params = {
      'performed_by_id': request['performed_by_id'],
      'organization_id': request['service_provider_id'],
      'port_id': request['port_id'],
      'trade_type': request['trade_type']
    }
    organization.create_organization_serviceable_port(params)


@celery.task()
def update_multiple_service_objects(object):
  get_multiple_service_objects(object)

@celery.task()
def send_closed_notifications_to_sales_agent_function(object):
    object.send_closed_notifications_to_sales_agent()

@celery.task()
def send_create_notifications_to_supply_agents_function(object):
    object.send_create_notifications_to_supply_agents()

@celery.task()
def send_notifications_to_supply_agents_local_request(object):
    object.send_notifications_to_supply_agents()

@celery.task()
def create_communication_background(data):
    common.create_communication(data)

@celery.task()
def send_fcl_freight_rate_task_notification(task_id):
    send_fcl_freight_rate_task_notification(task_id)


@celery.task()
def send_closed_notifications_to_sales_agent_local_request(object):
    object.send_closed_notifications_to_sales_agent()

@celery.task()
def send_closed_notifications_to_sales_agent_free_day_request(object):
    object.send_closed_notifications_to_sales_agent()

@celery.task()
def send_closed_notifications_to_sales_agent_feedback(object):
    object.send_closed_notifications_to_sales_agent()




@celery.task()
def bulk_operation_perform_action_functions(action_name,object,sourced_by_id,procured_by_id,cogo_entity_id):
    eval(f"object.perform_{action_name}_action(sourced_by_id='{sourced_by_id}',procured_by_id='{procured_by_id}',cogo_entity_id='{cogo_entity_id}')")


@celery.task()
def update_freight_objects_for_commodity_surcharge(surcharge_object):

    surcharge_object.update_freight_objects()


@celery.task()
def create_fcl_freight_rate_feedback_for_prediction(result):
    with db_cogo_lens.atomic() as transaction:
        try:
            for feedback in result:
                if "origin_country_id" not in feedback:
                    feedback["origin_country_id"] = None
                if "destination_country_id" not in feedback:
                    feedback["destination_country_id"] = None
                record = {
                    "origin_port_id": feedback["origin_port_id"],
                    "destination_port_id": feedback["destination_port_id"],
                    "origin_country_id": feedback["origin_country_id"],
                    "destination_country_id": feedback["destination_country_id"],
                    "shipping_line_id": feedback["shipping_line_id"],
                    "container_size": feedback["container_size"],
                    "container_type": feedback["container_type"],
                    "commodity": feedback["commodity"],
                    "validity_start": feedback['validities'][0]["validity_start"],
                    "validity_end": feedback['validities'][0]["validity_end"],
                    "predicted_price_currency": "USD",
                    "predicted_price": feedback["validities"][0]['line_items'][0]['price'] if ("validities" in feedback) and (feedback['validities']) else None,
                    "actual_price": feedback["actual_price"] if "actual_price" in feedback else None,
                    "actual_price_currency": feedback["actual_price_currency"] if "actual_price_currency" in feedback else None,
                    "source" : "predicted_for_rate_cards",
                    "creation_id" : feedback["id"],
                    "importer_exporter_id" : feedback['importer_exporter_id']
                }

                new_rate = FclRatePredictionFeedback.create(**record)
                feedback['id'] = new_rate.id

            c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)

            for val in result:
                if ("predicted_price" in val) and val['predicted_price']:
                    val["predicted_price"] = round(c.convert(val["predicted_price"], "USD", val["currency"], date=datetime.now()))
            return result

        except Exception as e:
            transaction.rollback()
            return e

# @celery.task()
# def update_expired_fcl_freight_rate_price():
#     ides = get_expired_fcl_freight_rates()
#     print("This is ids we got from expired",ides)
#     for req in ides:
#         req['procured_by_id'] = "d862bb07-02fb-4adc-ae20-d6e0bda7b9c1"
#         req['sourced_by_id'] = "7f6f97fd-c17b-4760-a09f-d70b6ad963e8"
#         req['performed_by_id'] = "039a0141-e6f3-43b0-9c51-144b22b9fc84"
#         req['schedule_type'] = "transhipment"
#         req['payment_term'] = "prepaid"
#         try:
#             update_expired_fcl_freight_rate_platform_prices(req)
#             return 'sucess'
#         except:
#             return 'failure'
# celery.conf.beat_schedule = {
#     'update_expired_fcl_freight_rate_price': {
#         'task': 'celery_worker.update_expired_fcl_freight_rate_price',
#         'schedule': crontab(minute=5,hour=19)
#     }
# }
# celery.start
