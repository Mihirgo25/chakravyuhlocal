from services.fcl_freight_rate.models.fcl_freight_location_cluster import (
    FclFreightLocationCluster,
)
from services.fcl_freight_rate.models.fcl_freight_rate import (
    FclFreightRate,
)
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import (
    FclFreightLocationClusterMapping,
)
from datetime import datetime, timedelta
from configs.fcl_freight_rate_constants import (
    CRITICAL_PORTS_INDIA_VIETNAM,
    DEFAULT_RATE_TYPE,
)
from fastapi.encoders import jsonable_encoder


def fetch_all_base_port_ids():
    all_ports = [
        str(entry.base_port_id)
        for entry in FclFreightLocationCluster.select(
            FclFreightLocationCluster.base_port_id
        )
    ]
    return [port for port in all_ports if port not in (CRITICAL_PORTS_INDIA_VIETNAM)]

def get_critical_ports_extension_parameters():
    all_base_port_ids = fetch_all_base_port_ids()
    start_time = datetime.now()

    base_port_query = (
        FclFreightRate.select(
            FclFreightRate.origin_port_id, FclFreightRate.destination_port_id
        )
        .distinct()
        .where(
            FclFreightRate.updated_at > start_time - timedelta(hours=6),
            (
                (FclFreightRate.origin_port_id << CRITICAL_PORTS_INDIA_VIETNAM)
                & (FclFreightRate.destination_port_id << all_base_port_ids)
            )
            | (
                (FclFreightRate.origin_port_id << all_base_port_ids)
                & (FclFreightRate.destination_port_id << CRITICAL_PORTS_INDIA_VIETNAM)
            ),
            FclFreightRate.mode.not_in(["predicted", "cluster_extension"]),
            FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
            FclFreightRate.commodity == "general",
            FclFreightRate.container_type == "standard",
            FclFreightRate.last_rate_available_date
            > datetime.now().date() + timedelta(days=1),
        )
    )

    all_combinations = base_port_query.execute()

    if not all_combinations:
        return []

    all_updated_ports = []
    for row in all_combinations:
        all_updated_ports.append(str(row.origin_port_id))
        all_updated_ports.append(str(row.destination_port_id))

    query = (
        FclFreightLocationClusterMapping.select(
            FclFreightLocationClusterMapping.location_id,
            FclFreightLocationCluster.base_port_id,
        )
        .join(FclFreightLocationCluster)
        .where(FclFreightLocationCluster.base_port_id.in_(all_updated_ports))
    )

    location_mappings = jsonable_encoder(list(query.dicts()))

    extension_parameters = []
    for combo in all_combinations:
        origin_secondary_ports = [
            mapping["location_id"]
            for mapping in location_mappings
            if mapping["base_port_id"] == str(combo.origin_port_id)
        ]

        destination_secondary_ports = [
            mapping["location_id"]
            for mapping in location_mappings
            if mapping["base_port_id"] == str(combo.destination_port_id)
        ]

        request_data = {
            "start_time": start_time,
            "origin_port_id": str(combo.origin_port_id),
            "destination_port_id": str(combo.destination_port_id),
            "container_type": "standard",
            "commodity": "general",
            "origin_secondary_ports": origin_secondary_ports,
            "destination_secondary_ports": destination_secondary_ports,
        }
        extension_parameters.append(request_data)

    return extension_parameters
