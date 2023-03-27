from datetime import date
from peewee import fn
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
# from celery_worker import celery
import pandas as pd
from datetime import datetime,timedelta
import datetime
from database.db_session import db

def create_audit(request):
    audit_data = {}
    freight = FclFreightRate.get_by_id(request['id'])
    freight_id = freight.id
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()
    line_items = freight.get_line_items()
    audit_data['line_items'] = line_items
    w_limit = freight.get_weight_limit()
    audit_data['weight_limit'] = w_limit
    o_local = freight.get_origin_local()
    audit_data['origin_local'] = o_local
    d_local = freight.get_destination_local()
    audit_data['destination_local'] = d_local

    FclFreightRateAudit.create(
        bulk_operation_id = request.get('bulk_operation_id'),
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data,
        object_id = freight_id,
        object_type = 'FclFreightRate'
    )


# def validate_freight_params(request):
#     if request.get('validity_start') or request.get('validity_end') or request.get('line_items'):
#         keys = ['validity_start', 'validity_end', 'line_items']
#         for key in keys:
#             if not request.get(key):
#                 HTTPException(status_code=499, detail="{key} is blank")

def update_expired_fcl_freight_rate_platform_prices(request):
    request['validity_start'] = datetime.datetime.now()
    request["validity_end"] = request["validity_start"]+ timedelta(days=14)
    with db.atomic() as transaction:
      try:
            fa = execute_transaction_code(request) 
            return fa
      except Exception as e:
            transaction.rollback()
            return e
def validate_freight_params(request):
  if request.get('validity_start') or request.get('validity_end'):
    keys = ['validity_start', 'validity_end']
    for key in keys:
      if not request.get(key):
        HTTPException(status_code=499, detail="{key} is blank")
def execute_transaction_code(request):
    validate_freight_params(request)
    freight_object = FclFreightRate.get_by_id(request['id'])
    # freight_object.set_source_to_predicted()
    if request.get('validity_start'):
        freight_object.validate_validity_object(request['validity_start'], request['validity_end'])
        validity_obj = freight_object.validities[0]
        freight_object.update_platform_prices_based_on_prediction_model()
        freight_object.validate_line_items(validity_obj['line_items'])
        freight_object.set_validities(request.get('validity_start').date(), request.get('validity_end').date(), validity_obj['line_items'], request.get('schedule_type'), False, request.get('payment_term'))
        freight_object.set_last_rate_available_date()
        freight_object.set_platform_prices()
    # freight_object.validate_before_save()
    freight_object.mode_to_predicted()
    try:
      freight_object.save()
      print("jhasdfjksdhfjkas")
    except Exception as e:
        raise HTTPException(status_code=499, detail='rate did not save')
    create_audit(request)
    return {
      'id': freight_object.id
    }

