from configs.env import *

def get_instance_url(service_name=None):
    if APP_ENV == 'development':
        url = RUBY_ADDRESS_URL
        if service_name in ["organization", "partner", "user"]:
            url = url + "/{}".format(service_name)
        return url
    service_port = COMMON_SERVICE_PORT
    if service_name in ['organization', 'user', 'lead', 'partner']:
        service_port = AUTH_SERVICE_PORT
    if service_name == 'location':
        service_port = COGOMAPS_SERVICE_PORT
    if service_name == 'spot_search':
        service_port = SPOT_SEARCH_PORT
    if service_name == 'checkout':
        service_port = CHECKOUT_PORT
    if service_name == 'shipment':
        service_port = SHIPMENT_PORT


    if service_name == 'common':
        instance_url = "http://{}:{}".format(INTERNAL_NLB, service_port)
    else:
        instance_url = "http://{}:{}/{}".format(INTERNAL_NLB, service_port, service_name)
    return instance_url
