from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster

def get_fcl_freight_commodity_cluster(request):
    commodity_cluster = get_commodity_cluster(request)
    return commodity_cluster

def get_commodity_cluster(request):
    response = FclFreightCommodityCluster.select().where(FclFreightCommodityCluster.id == request.get('id')).dicts().get()
    return response