from services.nandi.models.draft_fcl_freight_rate_local import DraftFclFreightRateLocal
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_local import get_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from services.nandi.interactions.create_draft_fcl_freight_rate_local import create_draft_fcl_freight_rate_local_data

def check_fcl_freight_rate_local_for_draft(request):
    if not request.get('rate_type'):
        request['rate_type'] = 'market_place'
    rate_exists_response = get_draft_rate_with_shipment_id(request)
    if rate_exists_response == False:
        fcl_freight_local = get_fcl_freight_rate_local(request)
        if 'id' not in fcl_freight_local:
            fcl_freight_local = create_fcl_freight_rate_local(request)
        else:
            if matching_local_charges(fcl_freight_local, request['data'].get('line_items')):
                return "Rate Already Exists"
        request['rate_id'] = fcl_freight_local.get('id')
        draft_fcl_freight_local = create_draft_fcl_freight_rate_local_data(request)
        return draft_fcl_freight_local
    return rate_exists_response

def get_draft_rate_with_shipment_id(request):
    rate = DraftFclFreightRateLocal.select().where(
        DraftFclFreightRateLocal.shipment_serial_id == request.get('shipment_serial_id')
    ).first()

    if not rate:
        return False

    if rate.status != 'pending':
        rate.status = 'pending'

    invoice_date = rate.invoice_date
    invoice_url = rate.invoice_url

    invoice_date.append(request['invoice_date'])
    invoice_url.append(request['invoice_url'])

    rate.invoice_date = invoice_date
    rate.invoice_url = invoice_url

    existing_line_items = (rate.data or {}).get('line_items', [])
    new_line_items = (request.get('data') or {}).get('line_items', [])

    merged_line_items = remove_duplicate_line_items(existing_line_items + new_line_items)
    rate.data = rate.data | ({'line_items' : merged_line_items})
    rate.save()

    return {'id':rate.id}

def matching_local_charges(fcl_freight_local, invoice_line_items = []):
    local_charges_dict = {}
    invoice_charges_dict = {}

    for charge in fcl_freight_local['line_items']:
        local_charges_dict[charge.get('code')] = charge.get('price')

    for invoice_charge in invoice_line_items:
        invoice_charges_dict[invoice_charge.get('code')] = invoice_charge.get('price')

    if len(local_charges_dict.keys()) == len(invoice_charges_dict.keys()):
        for charge_code, price in invoice_charges_dict.items():
            if charge_code not in local_charges_dict and price != local_charges_dict.get(charge_code):
                return False
    else:
        return False
    return True

def remove_duplicate_line_items(data):
    unique_items = {}
    for item in data:
        unique_items[item["code"]] = item

    unique_data = list(unique_items.values())
    return unique_data