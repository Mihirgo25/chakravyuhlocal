from services.rate_sheet.models.rate_sheet import RateSheet
import services.rate_sheet.interactions.fcl_rate_sheet_converted_file as process_rate_sheet
from services.rate_sheet.interactions.send_rate_sheet_notification import send_rate_sheet_notifications

from services.rate_sheet.helpers import *

def validate_and_process_rate_sheet_converted_file(params):
    update = RateSheet.get(RateSheet.id == params['id'])
    for converted_file in params['converted_files']:
        reset_counters(params, converted_file)
        getattr(process_rate_sheet, "process_{}_{}".format(converted_file['service_name'], converted_file['module']))(
            params, converted_file, update
        )
    update.converted_files = params.get('converted_files')
    update.save()
    for converted_file in params['converted_files']:
        delete_temp_data(converted_file)
    send_rate_sheet_notifications(params)
    return params
