from database.rails_db import *

def validate_shipping_line(model):
        shipping_line_data = get_operators(id=model.shipping_line_id)
        if (len(shipping_line_data) != 0) and shipping_line_data[0].get('operator_type') == 'shipping_line':
            model.shipping_line = shipping_line_data[0]
            return True
        return False
    
def handle_empty_ids(hash):
    for key, value in hash.items():
        if key.endswith('_id') or key == 'id':
            if isinstance(value, list):
                hash[key] = [id or None for id in value]
            else:
                hash[key] = value or None
    return hash



