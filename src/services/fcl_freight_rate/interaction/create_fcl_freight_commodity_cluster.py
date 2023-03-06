from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from fastapi import FastAPI, HTTPException
import datetime
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize

def create_fcl_freight_commodity_cluster(request):
    row = {
        'name' : request['name']
    }
    fcl_freight_commodity_cluster = find_or_initialize(FclFreightCommodityCluster,**row)

    fcl_freight_commodity_cluster.commodities = request['commodities']
    fcl_freight_commodity_cluster.status = 'active'

    fcl_freight_commodity_cluster.validate()

    if not fcl_freight_commodity_cluster.save(request):
        raise HTTPException(status_code=422, detail="Commodity Cluster not saved")

    return {'id' : fcl_freight_commodity_cluster.id}
