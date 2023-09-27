from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from micro_services.client import organization
from database.db_session import rd
from libs.parse_numeric import parse_numeric
from libs.csv_link_generator import get_csv_url
from playhouse.postgres_ext import ServerSide
from playhouse.shortcuts import model_to_dict

def update_organization_fcl_customs(request):
    query = FclCustomsRate.select(
                FclCustomsRate.id
            ).where(
                FclCustomsRate.service_provider_id == request.get("service_provider_id"), 
                FclCustomsRate.rate_not_available_entry == False, 
                FclCustomsRate.rate_type == DEFAULT_RATE_TYPE).exists()

    if not query:
        params = {
            "id" : request.get("service_provider_id"), 
            "customs_rates_added" : True
        }
        organization.update_organization(params)

def generate_csv_file_url_for_fcl_customs(query):
    csv_urls = []
    rate_count = 0
    final_data = []

    for rate in ServerSide(query):
        if rate_count > 5000:
            rate_count = 0
            csv_url = get_csv_url("fcl_customs", final_data)
            csv_urls.append(csv_url)
            final_data = []


        rate_data = model_to_dict(rate)
        required_coverage_data = get_fcl_customs_coverage_required_data(rate_data)
        final_data.append(required_coverage_data)
        rate_count += 1

    if final_data:
        csv_url = get_csv_url("fcl_customs", final_data)
        csv_urls.append(csv_url)

    return {"urls": csv_urls}
                         
        

def get_fcl_customs_coverage_required_data(coverage_data):
    required_data = {}
    required_data['location'] = coverage_data['location']['name']
    required_data['port_code'] = coverage_data['location']['port_code']
    required_data['commodity'] = coverage_data['commodity']
    required_data['container_type']  = coverage_data['container_type']
    required_data['container_size'] = coverage_data['container_size']
    required_data['service_provider'] = coverage_data['service_provider']['short_name'] if coverage_data.get('service_provider') else None
    return required_data
