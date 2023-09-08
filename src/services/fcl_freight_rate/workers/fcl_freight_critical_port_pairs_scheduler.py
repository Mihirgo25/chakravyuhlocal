from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_job import create_fcl_freight_rate_job
from configs.fcl_freight_rate_constants import CRITICAL_PORTS_INDIA_VIETNAM, DEFAULT_RATE_TYPE
from services.air_freight_rate.constants.air_freight_rate_constants import CRITICAL_AIRPORTS_INDIA_VIETNAM
import datetime
from playhouse.postgres_ext import ServerSide
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from fastapi.encoders import jsonable_encoder
from playhouse.shortcuts import model_to_dict

SEVEN_DAYS_AGO = datetime.datetime.now().date() - datetime.timedelta(days=7)

REQUIRED_COLUMNS = ['id', 'origin_port_id', 'origin_port', 'origin_main_port_id', 'destination_port_id', 'destination_port','destination_main_port_id',
                        'shipping_line_id', 'shipping_line', 'service_provider_id', 'service_provider','container_size', 'container_type', 'commodity', 'rate_type']

def fcl_freight_critical_port_pairs_scheduler():
    all_fcl_critical_ports = FclFreightLocationCluster.select(FclFreightLocationCluster.base_port_id)
    all_fcl_critical_ports = jsonable_encoder(list(all_fcl_critical_ports.dicts()))
    fcl_critical_ports_except_in_vn = [str(i['base_port_id']) for i in all_fcl_critical_ports if str(i['base_port_id']) not in CRITICAL_AIRPORTS_INDIA_VIETNAM]

    fcl_query = FclFreightRate.select(*[getattr(FclFreightRate, col) for col in REQUIRED_COLUMNS]).where(
            ((FclFreightRate.origin_port_id << CRITICAL_PORTS_INDIA_VIETNAM) & (FclFreightRate.destination_port_id << fcl_critical_ports_except_in_vn)) | ((FclFreightRate.origin_port_id << fcl_critical_ports_except_in_vn) & (FclFreightRate.destination_port_id << CRITICAL_PORTS_INDIA_VIETNAM)),
            (FclFreightRate.updated_at.cast('date') == SEVEN_DAYS_AGO),
            FclFreightRate.mode.not_in(['predicted', 'cluster_extension']),
            FclFreightRate.rate_type == 'market_place'
        )
            
    for rate in ServerSide(fcl_query):
        rate_data = model_to_dict(rate)
        create_fcl_freight_rate_job(rate_data, 'critical_ports')
        