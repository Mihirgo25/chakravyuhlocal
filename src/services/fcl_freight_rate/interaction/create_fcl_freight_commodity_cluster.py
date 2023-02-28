from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
 
def find_or_initialize(**kwargs):
    fcl_freight_commodity_cluster = FclFreightCommodityCluster.find_by(**kwargs)
    if fcl_freight_commodity_cluster:
        return fcl_freight_commodity_cluster
    else:
        return FclFreightCommodityCluster.create(**kwargs)

def create_fcl_freight_commodity_cluster(request):
    row = {
        'name' : request['name']
    }
    fcl_freight_commodity_cluster = FclFreightCommodityCluster.find_or_initialize(**row)
    fcl_freight_commodity_cluster.update(**get_create_params())

    if not fcl_freight_commodity_cluster.save():
        raise HTTPException(status_code=422, detail="Commodity Cluster not saved")

    return {'id' : fcl_freight_commodity_cluster.id}

def get_create_params(self):
    return {
        'commodities': self.commodities,
        'status': 'active'
    }
