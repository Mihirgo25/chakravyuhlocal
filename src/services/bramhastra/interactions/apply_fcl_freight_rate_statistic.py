from services.bramhastra.helpers.fcl_freight import Rate, FclFreight
from services.bramhastra.enums import ValidityAction
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping


def apply_fcl_freight_rate_statistic(request):
    if request.action == 'create':
        create_fcl_freight_rate_statistic(request.create_params)
    elif request.action == 'update':
        update_fcl_freight_rate_statistic(request.update_params)
    else:
        raise ValueError("send create or update freight parameters")


def create_fcl_freight_rate_statistic(params):
    rate = FclFreight(freight=params.freight)
    rate.
    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

    FclFreightRate.delete().where(FclFreightRate.id == params.freight.rate_id).execute()


def update_fcl_freight_rate_statistic(params):
    pass 


def add_pricing_zone_map_ids(origin_port_id, destination_port_id):
    FclFreightLocationClusterMapping.select().where(FclFreightLocationClusterMapping.location_id.in_([origin_port_id,destination_port_id]))
    
