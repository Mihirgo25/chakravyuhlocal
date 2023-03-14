from rails_client import client
from datetime import datetime
from models.fcl_freight_rates import FclFreightRate
from interaction.create_fcl_freight_rate import find_or_initialize 
from configs.fcl_freight_rate_constants import SCHEDULE_TYPES,PAYMENT_TERM,SPECIFICITY_TYPE
import json
from interaction.create_fcl_freight_rate_local import find_or_initialize as fcl_freight_rate_local_instance
from interaction.create_fcl_freight_rate_free_day import find_or_initialize as fcl_freight_rate_free_days_instance
class ValidateFclFreightObject:
    module :str
    object :dict



    def execute(self):
        rate_object  = eval(f"get_{self.module}_object")


    def get_freight_object(self):
        for port in ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port']:
            self.object[f"{port}_id"] = self.get_port_id(self.object[port])

            del self.object[port]
        self.object['shipping_line_id'] = self.get_shipping_line_id(self.object['shipping_line'])

        del self.object['shipping_line']

        try:
            self.object['validity_start'] = datetime.strptime(self.object['validity_start'], '%Y-%m-%d').date()
            self.object['validity_end'] = datetime.strptime(self.object['validity_end'], '%Y-%m-%d').date()
        except Exception as e:
            self.object['validity_start'] = None
            self.object['validity_end'] = None


        rate_object_data = {
            "origin_port_id" :self.object['origin_port_id'],
            "origin_main_port_id":self.object['origin_main_port_id'],
            "destination_port_id":self.object['destination_port_id'],
    "destination_main_port_id":self.object['destination_main_port_id'],
    "container_size":self.object['container_size'],
    "container_type":self.object['container_type'],
    "commodity":self.object['commodity'],
    "shipping_line_id":self.object['shipping_line_id'],
    "service_provider_id":self.object['service_provider_id'],
    "importer_exporter_id":self.object['importer_exporter_id'],
    "cogo_entity_id":self.object['cogo_entity_id'],
    "rate_not_available_entry":False
        }

        rate_object = find_or_initialize(**rate_object_data)

        rate_object.validate_validity_object(self.object['validity_start'],self.object['validity_end'])

        for line_item in self.object['line_items']:
            try:
                float(line_item['price'])
            except Exception as e:
                raise  f"{line_item['price']} is Invalid"
        
        if self.object.get(['schedule_type']) and self.object['schedule_type'] not in SCHEDULE_TYPES:
            raise f"{self.object['schedule_type']} is invalid, valid schedule types are {SCHEDULE_TYPES}"

        if self.object.get(['payment_term']) and self.object['payment_term'] not in PAYMENT_TERM:
            raise f"{self.object['payment_term']} is invalid, valid paymenet terms are {PAYMENT_TERM}"
        
        rate_object.validate_line_items(self.object['line_items'])
        rate_object.weight_limit= self.object['weight_limit']
        rate_object.destination_local = json.dump(json.loads(rate_object.destination_local) | self.object['destination_local'])

        return rate_object

    
    def get_local_object(self):
        for port in ['port', 'main_port']:
            self.object[f"{port}_id"] = self.get_port_id(self.object[port])

            del self.object[port]
        
        for line_item in self.object['data']['line_items']:
            line_item.update({'location_item':self.get_location_id(line_item['location'])})
        
        local__data = {
            "port_id" : self.object['port_id'],
            "trade_type" : self.object['trade_type'],
            "main_port_id" : self.object['main_port_id'],
            "container_size" : self.object['container_size'],
            "container_type" : self.object['container_type'],
            "commodity" :self.object['commodity'],
            "shipping_line_id" : self.object['shipping_line_id'],
            "service_provider_id": self.object['service_provider_id']
        }
        local = fcl_freight_rate_local_instance(**local__data)

        for line_item in self.object['data']['line_items']:
            try:
                float(line_item['price'])
            except Exception as e:
                return  f"{line_item['price']} is Invalid"

        local.data = json.dump(json.loads(local.data) | self.object['data'])

        return local

    def get_free_day_object(self):
        location = self.get_location(self.object["location"], self.object["location_type"])

        try:
            self.object['port_id'] = location['seaport_id']
        except:
            self.object['port_id'] = None
        
        try:
            self.object['country_id'] = location['country_id']
        except:
            self.object['country_id'] = None
        
        try:
            self.object['trade_id'] = location['trade_id']
        except:
            self.object['trade_id'] = None
        
        try:
            self.object['continent_id'] = location['continent_id']
        except:
            self.object['continent_id'] = None
        
        del self.object['location']

        self.object['shipping_line_id'] = self.get_shipping_line_id(self.object['shipping_line'])

        del self.object['shipping_line']

        try:
            self.object["importer_exporter_id"] = self.get_importer_exporter_id(self.object["importer_exporter"])
        except :
            self.object["importer_exporter_id"] = None

        del self.object["importer_exporter"]

        free_day_data = {
            "location_id":self.object['location_id'],
            "trade_type":self.object['trade_type'],
            "container_size":self.object['container_size'],
            "container_type":self.object['container_type'],
            "shipping_line_id":self.object['shipping_line_id'],
            "service_provider_id":self.object['service_provider_id'],
            "specificity_type":self.object['specificity_type'],
            "free_days_type":self.object['free_days_type'],
            "importer_exporter_id":self.object['importer_exporter_id']
        }
        
        free_day = fcl_freight_rate_free_days_instance(**free_day_data)

        for item,value in self.object:
            setattr(free_day,item,value)
        
        if not self.object.get(['location_id']):
            raise f"location_id is invalid"
        
        if not self.object.get(['shipping_line_id']):
            raise f"shipping_line_id is invalid"
        
        if self.object.get(['specificity_type']) not in SPECIFICITY_TYPE:
            raise f"specificity_type is invalid"

        return free_day

        
    def get_port_id(port_code):
        request = {
           "filters":{ "type" : 'seaport',
            "port_code": port_code}
        }
        locations = client.ruby.list_locations(request)

        return locations
    
    def get_shipping_line_id(shipping_line):
        print()
    
    def get_location_id():
        print()

    def get_location():
        print()

        


