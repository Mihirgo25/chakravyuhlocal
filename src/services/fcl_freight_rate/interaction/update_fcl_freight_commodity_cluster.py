from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from services.fcl_freight_rate.interaction.create_fcl_freight_commodity_cluster import create_fcl_freight_commodity_cluster
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit

def find_or_initialize(**kwargs):
    fcl_freight_commodity_cluster = FclFreightCommodityCluster.find_by(**kwargs)
    if fcl_freight_commodity_cluster:
        return fcl_freight_commodity_cluster
    else:
        return FclFreightCommodityCluster.create(**kwargs)
    
def update_fcl_freight_commodity_cluster(request):
    fcl_freight_commodity_cluster = FclFreightCommodityCluster.get_by_id(request['id'])
    if not fcl_freight_commodity_cluster:
        raise HTTPException(status_code=404, detail="Commodity Cluster not found")
    
    update_params = {key: value for key, value in request.items() if key in ['name', 'commodities', 'status']}
    
    if not fcl_freight_commodity_cluster.update(**update_params):
        raise HTTPException(status_code=422, detail="Commodity Cluster not updated")
    
    return {'id' : fcl_freight_commodity_cluster.id}
