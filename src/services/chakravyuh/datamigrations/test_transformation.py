from services.chakravyuh.setters.fcl_freight import FclFreightVyuh as FclFreightVyuhSetter
from fastapi.encoders import jsonable_encoder
import datetime

test_key = {
    'new_rate': {
        'origin_port_id': '47283fd0-313e-4261-b53e-585d18073ca6', 
        'destination_port_id': 'a590bda5-374d-482a-888b-0ad0adbe62d9', 
        'container_size': '20', 
        'container_type': 'standard', 
        'commodity': 'general', 
        'shipping_line_id': '2d477bb2-8956-4dbe-bd8b-71144b60374c', 
        'service_provider_id': '5dc403b3-c1bd-4871-b8bd-35543aaadb36', 
        'validity_start': datetime.datetime(2023, 5, 9, 0, 0, tzinfo=datetime.timezone.utc), 
        'validity_end': datetime.datetime(2023, 5, 31, 4, 50, tzinfo=datetime.timezone.utc), 
        'schedule_type': 'direct', 
        'payment_term': 'prepaid', 
        'line_items': [{'code': 'BAS', 'unit': 'per_container', 'price': 2350.0, 'currency': 'USD', 'slabs': []}], 
        'performed_by_id': '1eb3f218-0aee-4189-9ab0-001e0851d682', 
        'procured_by_id': '1eb3f218-0aee-4189-9ab0-001e0851d682', 
        'sourced_by_id': 'fbd1df15-8de7-4784-829c-f1026f5572cc', 
        'source': 'flash_booking', 
        'origin_main_port_id': 'c4301086-92a8-463d-af00-9c1222ff223f', 
        'destination_main_port_id': None, 
        'importer_exporter_id': None, 
        'cogo_entity_id': None, 
        'mode': 'rate_extension', 
        'accuracy': 100, 
        'origin_location_ids': ['47283fd0-313e-4261-b53e-585d18073ca6', '541d1232-58ce-4d64-83d6-556a42209eb7', 'd1e7b3ca-7518-4706-a644-e99d3aa2e0a9', 'a5fad8d7-ea33-4dab-82d6-e7097fbffee1'], 
        'destination_location_ids': ['a590bda5-374d-482a-888b-0ad0adbe62d9', '71bde190-f4ce-464b-b71b-c0935c1308c6', '0b1e8fcd-702f-4fb0-a2bd-408133bb013c', '0168d0ca-8666-423b-9900-9e362ae8e4a0'], 
        'id': '5a88e53a-ebb3-4079-977a-e4e2cc2fe8f3', 
        'origin_country_id': '541d1232-58ce-4d64-83d6-556a42209eb7', 
        'destination_country_id': '71bde190-f4ce-464b-b71b-c0935c1308c6', 
        'origin_trade_id': 'd1e7b3ca-7518-4706-a644-e99d3aa2e0a9', 
        'destination_trade_id': '0b1e8fcd-702f-4fb0-a2bd-408133bb013c'
        }, 
    'current_validities': [{'validity_start': '2023-05-09', 'validity_end': '2023-05-31', 'line_items': [{'code': 'BAS', 'unit': 'per_container', 'price': 2350.0, 'currency': 'USD', 'slabs': []}], 'price': 2350.0, 'currency': 'USD', 'schedule_type': 'transhipment', 'payment_term': 'prepaid', 'likes_count': 0, 'dislikes_count': 0, 'id': '85e638bc-8d7b-4e1c-aff3-ecc205136c2c', 'platform_price': 2350.0}]
    }

def test_transformation():
    new_rate = test_key['new_rate']
    current_validities = test_key['current_validities']
    fcl_freight_vyuh = FclFreightVyuhSetter(new_rate=new_rate, current_validities=current_validities)
    fcl_freight_vyuh.set_dynamic_pricing()


