from services.fcl_freight_rate.interaction.get_cluster_extension_gri_worker import get_cluster_extension_gri_worker
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping
import datetime

INDIA_CRITICAL_PORTS = ['eb187b38-51b2-4a5e-9f3c-978033ca1ddf','7aa6ac82-c295-497f-bfe1-90294cdfa7a9','3c843f50-867c-4b07-bb57-e61af97dabfe']
VIETNAM_CRITICAL_PORTS = ['b0a48e84-48d5-438b-841a-e800fb68e439','c2d6fb91-2875-4d73-b12b-dd1b78fdfe8a','76fdeee3-1c7f-4f6e-a5d2-2a729445f2d9']

def fetch_all_base_port_ids():
    all_ports = [str(entry.base_port_id) for entry in FclFreightLocationCluster.select(FclFreightLocationCluster.base_port_id)]
    return [port for port in all_ports if port not in (INDIA_CRITICAL_PORTS + VIETNAM_CRITICAL_PORTS)]

def generate_combinations(base_port_ids, critical_ports):
    combinations = []
    
    for port in critical_ports:
        for base_port in base_port_ids:
            combinations.append({
                "origin_port_id": port,
                "destination_port_id": base_port
            })

    for base_port in base_port_ids:
        for port in critical_ports:
            combinations.append({
                "origin_port_id": base_port,
                "destination_port_id": port
            })
    
    return combinations
def get_critical_ports_extension_parameters():
    all_base_port_ids = fetch_all_base_port_ids()
    india_combinations = generate_combinations(all_base_port_ids, INDIA_CRITICAL_PORTS)
    vietnam_combinations = generate_combinations(all_base_port_ids, VIETNAM_CRITICAL_PORTS)
    starttime = datetime.datetime.now()
    
    location_mappings = (FclFreightLocationClusterMapping
                             .select(FclFreightLocationClusterMapping.location_id, FclFreightLocationCluster.base_port_id)
                             .join(FclFreightLocationCluster))
    
    
    extension_parameters = []
    for combo in india_combinations + vietnam_combinations:
        origin_secondary_ports = [str(mapping.location_id) for mapping in location_mappings if str(mapping.base_port_id) == combo["origin_port_id"] ]

        request_data = {
            "start_time": starttime,
            "origin_port_id": combo["origin_port_id"],
            "destination_port_id": combo["destination_port_id"],
            "container_type": "standard",
            "commodity": "general",
            "origin_secondary_ports": origin_secondary_ports,
        }
        extension_parameters.append(request_data)

    return extension_parameters
