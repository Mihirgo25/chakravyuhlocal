from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster

def get_fcl_freight_commodity_cluster(id):
    commodity_cluster = get_commodity_cluster(id)
    return commodity_cluster

def get_commodity_cluster(id):
    try:
        response = FclFreightCommodityCluster.select().where(FclFreightCommodityCluster.id == id).dicts().get()
    except:
        response = {}
    return response