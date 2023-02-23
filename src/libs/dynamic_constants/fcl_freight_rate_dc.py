from rails_client import client

class FclFreightRateDc:
    @classmethod
    def get_key_value(cls, key_name, params = {}):
        constant_data = client.ruby.get_platform_config_constant({'key_name': key_name, 'service': 'FclFreightRate'})
        method_name = f'get_{key_name.lower()}'
        data = getattr(cls, method_name)(constant_data, params)
        return data
    
    @classmethod
    def get_default_local_agent_id(cls ,data, params):
        filtered_data = cls.get_filtered_data(data, params)

        return filtered_data[0].get('value')

    @classmethod
    def get_default_service_provider_id(cls, data, params):
        filtered_data = cls.get_filtered_data(data, params)

        return filtered_data[0].get('value')

    @classmethod
    def get_default_sourced_by_id(cls, data, params):
        filtered_data = cls.get_filtered_data(data, params)

        return filtered_data[0].get('value')

    @classmethod
    def get_default_procured_by_id(cls, data, params):
        filtered_data = cls.get_filtered_data(data, params)

        return filtered_data[0].get('value')
  
    @classmethod
    def get_role_ids_for_notifications(cls, data, params):
        filtered_data = cls.get_filtered_data(data, params)

        return filtered_data[0].get('value')

    @staticmethod
    def get_filtered_data(data, params):
        filtered_data = [t for t in data if t['cogo_entity_id'] == params['cogo_entity_id'] and t['country_id'] == params['country_id'] and t['persona'] == params['persona'] and t['service_type'] == params['service_type']]

        if not filtered_data:
            filtered_data = [t for t in data if t['value_type'] == 'default']
    
        return filtered_data