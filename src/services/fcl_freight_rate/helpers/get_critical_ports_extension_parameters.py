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
    DEFAULT_SERVICE_PROVIDER_ID,
)
from fastapi.encoders import jsonable_encoder
from peewee import SQL


def fetch_all_base_port_ids():
    all_ports = [
        str(entry.base_port_id)
        for entry in FclFreightLocationCluster.select(
            FclFreightLocationCluster.base_port_id
        )
    ]
    return [port for port in all_ports if port not in CRITICAL_PORTS_INDIA_VIETNAM]


def get_critical_ports_extension_parameters():
    all_base_port_ids = fetch_all_base_port_ids()
    last_updated_at = datetime.now() - timedelta(days=1)

    base_port_query = (
        FclFreightRate.select(
            FclFreightRate.origin_port_id, FclFreightRate.destination_port_id
        )
        .distinct()
        .where(
            FclFreightRate.updated_at > last_updated_at,
            (
                (FclFreightRate.origin_port_id << CRITICAL_PORTS_INDIA_VIETNAM)
                & (FclFreightRate.destination_port_id << all_base_port_ids)
            )
            | (
                (FclFreightRate.origin_port_id << all_base_port_ids)
                & (FclFreightRate.destination_port_id << CRITICAL_PORTS_INDIA_VIETNAM)
            ),
            FclFreightRate.mode.not_in(["predicted", "cluster_extension"]),
            FclFreightRate.service_provider_id != DEFAULT_SERVICE_PROVIDER_ID,
            FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
            FclFreightRate.commodity == "general",
            FclFreightRate.container_type == "standard",
            FclFreightRate.last_rate_available_date
            > datetime.now().date() + timedelta(days=1),
            ~FclFreightRate.service_provider["category_types"].contains("nvocc"),
            SQL(
                """
            NOT EXISTS (
                SELECT 1
                FROM jsonb_each_text(tags) AS kv
                WHERE kv.value = 'trend_GRI'
            )
            """
            ),
        )
    )

    latest_updated_port_pairs = base_port_query.execute()

    if not latest_updated_port_pairs:
        return []

    all_latest_updated_ports = []
    for row in latest_updated_port_pairs:
        all_latest_updated_ports.append(str(row.origin_port_id))
        all_latest_updated_ports.append(str(row.destination_port_id))

    cluster_mapping_query = (
        FclFreightLocationClusterMapping.select(
            FclFreightLocationClusterMapping.location_id,
            FclFreightLocationCluster.base_port_id,
        )
        .join(FclFreightLocationCluster)
        .where(FclFreightLocationCluster.base_port_id.in_(all_latest_updated_ports))
    )

    location_mappings = {}
    for row in jsonable_encoder(list(cluster_mapping_query.dicts())):
        if row["base_port_id"] in location_mappings:
            location_mappings[row["base_port_id"]].append(row["location_id"])
        else:
            location_mappings[row["base_port_id"]] = [row["location_id"]]

    extension_parameters = []
    for latest_updated_port_pair in latest_updated_port_pairs:
        request_data = {
            "last_updated_at": last_updated_at,
            "origin_port_id": str(latest_updated_port_pair.origin_port_id),
            "destination_port_id": str(latest_updated_port_pair.destination_port_id),
            "container_type": "standard",
            "commodity": "general",
            "origin_secondary_ports": location_mappings[
                str(latest_updated_port_pair.origin_port_id)
            ],
            "destination_secondary_ports": location_mappings[
                str(latest_updated_port_pair.destination_port_id)
            ],
        }
        extension_parameters.append(request_data)

    return extension_parameters
