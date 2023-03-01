from rails_client import client
from datetime import datetime
from models.fcl_freight_rates import FclFreightRate

class ValidateFclFreightObject:
    module :str
    object :dict



    def execute(self):
        rate_object  = eval("get_{self.module}_object")


    def get_freight_object(self):
        for port in ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port']:
            self.object[f"{port}_id"] = self.get_port_id(self.object[port])

            del self.object[port]
        self.object['shipping_line_id'] = self.get_shipping_line_id(self.object['shipping_line'])

        del self.object['shipping_line']

        self.object['validity_start'] = datetime.strptime(self.object['validity_start'], '%Y-%m-%d').date() 
        self.object['validity_end'] = datetime.strptime(self.object['validity_end'], '%Y-%m-%d').date()

        rate_object = FclFreightRate




        



    def get_port_id(port_code):
        request = {
           "filters":{ "type" : 'seaport',
            "port_code": port_code}
        }
        locations = client.ruby.list_locations(request)

        return locations
    
    def get_shipping_line_id(shipping_line):
        print()


