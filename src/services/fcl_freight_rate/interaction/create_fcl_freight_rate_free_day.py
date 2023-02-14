from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
import json
from fastapi import FastAPI, HTTPException
from operator import attrgetter
import datetime


def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRateFreeDay.get(**kwargs)
  except FclFreightRateFreeDay.DoesNotExist:
    obj = FclFreightRateFreeDay(**kwargs)
  return obj

def get_free_day_object(request):
    row = {
    'location_id' : request['location_id'],
    'trade_type' : request['trade_type'],
    'free_days_type' : request['free_days_type'],
    'container_type' : request['container_type'],
    'container_size' : request['container_size'],
    'shipping_line_id' : request['shipping_line_id'],
    'service_provider_id' : request['service_provider_id'],
    'specificity_type' : request['specificity_type']
  }
    if 'importer_exporter_id' in request:
       row['importer_exporter_id'] = request['importer_exporter_id']
    
    free_day_data = find_or_initialize(**row)
    print('find_or_init', free_day_data)

    extra_fields = ['previous_days_applicable','free_limit','remarks','slabs']
    for field in extra_fields:
       if field in request:
          var = attrgetter(field)(free_day_data) #remove var
          if var:
             if var != request[field]:
              setattr(free_day_data, field, request[field])
          else:
             setattr(free_day_data, field, request[field])

    for key in ['free_limit', 'remarks', 'slabs', 'previous_days_applicable']:
       if key in request:
          print('key',key)
          free_day_data.key = request[key]
    print('free_day_data', free_day_data.location_id,free_day_data.trade_type,free_day_data.free_days_type,free_day_data.container_type,free_day_data.container_size,free_day_data.shipping_line_id,free_day_data.service_provider_id,free_day_data.specificity_type,free_day_data.free_limit,free_day_data.previous_days_applicable)
    free_day_data.rate_not_available_entry = False

    return free_day_data

# def create_audit(request, freight_id):

#     audit_data = {}
#     audit_data['validity_start'] = request['validity_start'].isoformat()
#     audit_data['validity_end'] = request['validity_end'].isoformat()
#     audit_data['line_items'] = request['line_items']
#     audit_data['weight_limit'] = request['weight_limit']
#     audit_data['origin_local'] = request.get('origin_local')
#     audit_data['destination_local'] = request.get('destination_local')

#     FclFreightRateAudit.create(
#         bulk_operation_id = request.get('bulk_operation_id'),
#         rate_sheet_id = request.get('rate_sheet_id'),
#         action_name = 'create',
#         performed_by_id = request['performed_by_id'],
#         procured_by_id = request['procured_by_id'],
#         sourced_by_id = request['sourced_by_id'],
#         data = audit_data,
#         object_id = freight_id,
#         object_type = 'FclFreightRate'
#     )


def create_fcl_freight_rate_free_day(request):

    free_day = get_free_day_object(request)

    try:
      free_day.save()
    except:
      raise HTTPException(status_code=499, detail='fcl freight rate free day did not save')
    
    # free_day.update_special_attributes

    # create_audit(request, free_day.id)
    print('free_day.id', free_day)

    return {"id": free_day.id}
