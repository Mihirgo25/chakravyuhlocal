from configs.env import *
import boto3

client = boto3.client(
    'servicediscovery',
    region_name="ap-south-1",
    )

def get_instance_url(service_name=None):
    if APP_ENV == 'development':
        url = RUBY_ADDRESS_URL
        if service_name in ["organization", "partner"]:
            url = url + "/{}".format(service_name)
        return url
    service = COMMON_SERVICE_NAME
    if service_name in ['organization', 'user', 'lead', 'partner']:
        service = AUTH_SERVICE_NAME
    if service_name == 'location':
        service = COGOMAPS_SERVICE_NAME

    if service_name == 'location':
        instance_url = "http://{}:8104/{}".format(INTERNAL_NLB, service_name)
        return instance_url

    response = client.discover_instances(
        NamespaceName=MICRO_SERVICE_NAMESPACE,
        ServiceName=service,
        MaxResults=10,
        HealthStatus='HEALTHY',
        )
    service_ip_address = None
    service_port = None
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
