from configs.env import *
import boto3

client = boto3.client(
    'servicediscovery', 
    region_name="ap-south-1",
    )

def get_instance_url(service_name=None):
    if APP_ENV == 'development':
        return RUBY_ADDRESS_URL
    port = COMMON_SERVICE_PORT
    service = COMMON_SERVICE_NAME   
    if service_name in ['organization', 'user', 'lead', 'partner']:
        port = AUTH_SERVICE_PORT
        service = AUTH_SERVICE_NAME
    if service_name == 'location':
        port = COGOMAPS_SERVICE_PORT
        service = COGOMAPS_SERVICE_NAME
    
    if service_name == 'location':
        instance_url = "http://{}:{}/{}".format(INTERNAL_NLB, service_port, service_name)
        return instance_url
    
    response = client.discover_instances(
        NamespaceName=MICRO_SERVICE_NAMESPACE,
        ServiceName=service,
        MaxResults=10,
        HealthStatus='HEALTHY',
        )
    service_ip_address = None
    service_port = port
    try:
        attributes = response['Instances'][0]['Attributes']
        service_ip_address = attributes['AWS_INSTANCE_IPV4']
        service_port = attributes['AWS_INSTANCE_PORT']
    except Exception as e:
        print("Error in getting micro service", e)
    
    if service == 'rehnuma' or service_name == 'common':
        instance_url = "http://{}:{}".format(service_ip_address, service_port)
    else:
        instance_url = "http://{}:{}/{}".format(service_ip_address, service_port, service_name)
    return instance_url