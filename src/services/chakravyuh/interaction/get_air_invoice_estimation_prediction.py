from services.chakravyuh.setters.air_freight import AirFreightVyuh as AirFreightVyuhSetters
from database.rails_db import get_invoices

def invoice_rates_updation():
    freight_rates = get_invoices()
    for freight_rate in freight_rates:
        line_items = freight_rate['line_items']
        actual_lineitem = None
        bas_count = 0
        for line_item in line_items:
            if line_item['code'] == 'BAS' and line_item['unit'] == 'per_kg':
                actual_lineitem = line_item
                bas_count = bas_count + 1
            if line_item['code'] == 'BAS' and line_item['unit'] == 'per_shipment' and not actual_lineitem:
                actual_lineitem = line_item
                bas_count = bas_count + 1
                actual_lineitem['price'] = (line_item['price'] / (freight_rate['chargeable_weight'] or freight_rate['weight']))
        if actual_lineitem and bas_count == 1:
            freight_rate['price'] = actual_lineitem['price']
            freight_rate['unit'] = actual_lineitem['unit']
            freight_rate['currency'] = actual_lineitem['currency']
        if bas_count ==1:
            freight_rate['shipment_type'] = 'box'
            if freight_rate['packages']:
                package = freight_rate['packages'][0]
                freight_rate['shipment_type'] = package['packing_type']
            setter = AirFreightVyuhSetters(freight_rate)
            setter.set_dynamic_pricing()
    return True
    