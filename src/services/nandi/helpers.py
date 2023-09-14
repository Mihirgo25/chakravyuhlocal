from services.nandi.models.draft_fcl_freight_rate_local import DraftFclFreightRateLocal

def matching_local_charges(fcl_freight_local, invoice_line_items):
    local_charges_dict = {}
    invoice_charges_dict = {}
    check_list = []

    for charge in fcl_freight_local['line_items']:
        local_charges_dict[charge.get('code')] = charge.get('price')
    
    for invoice_charge in invoice_line_items:
        invoice_charges_dict[invoice_charge.get('code')] = invoice_charge.get('price')

    if len(local_charges_dict.keys()) == len(invoice_charges_dict.keys()):
        for charge_code, price in invoice_charges_dict.items():
            if charge_code in local_charges_dict and price == local_charges_dict.get(charge_code):
                check_list.append(True)
            else:
                return False
    else:
        return False
    return True

def get_rate_with_shipment_id(request):
    rate = DraftFclFreightRateLocal.select().where(
        DraftFclFreightRateLocal.shipment_serial_id == request.get('shipment_serial_id'),
        DraftFclFreightRateLocal.status == request.get('status','pending')
    ).execute()

    if not rate:
        return False
    
    rate.invoice_date.append(request['invoice_date'])
    rate.invoice_url.append(request['invoice_url'])
    line_items = rate.data.get('line_items')
    line_items.extend(request.get('line_items'))
    rate.data = rate.data | ({'line_items': line_items})
    rate.save()
    return rate.id