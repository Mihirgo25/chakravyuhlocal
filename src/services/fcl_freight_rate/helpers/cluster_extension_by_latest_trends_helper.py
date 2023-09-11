from services.fcl_freight_rate.helpers.get_critical_ports_extension_parameters import get_critical_ports_extension_parameters
from services.fcl_freight_rate.interaction.extend_cluster_rates_by_latest_trends import extend_cluster_rates_by_latest_trends
import asyncio

def cluster_extension_by_latest_trends_helper():     
    critical_port_pairs = get_critical_ports_extension_parameters()
    for request in critical_port_pairs:
        asyncio.run(extend_cluster_rates_by_latest_trends(request))