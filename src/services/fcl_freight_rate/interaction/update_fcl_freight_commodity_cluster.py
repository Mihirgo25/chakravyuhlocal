from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from services.fcl_freight_rate.interaction.create_fcl_freight_commodity_cluster import create_fcl_freight_commodity_cluster
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit


def update_fcl_freight_commodity_cluster(request):
   
    update_params = {key: value for key, value in request.items() if key in ['name', 'commodities', 'status']}

    fcl_freight_commodity_cluster = FclFreightCommodityCluster.update(update_params).where(FclFreightCommodityCluster.id == request['id'])

    if fcl_freight_commodity_cluster.execute() == 0:
        raise HTTPException(status_code=422, detail="Commodity Cluster not updated")
    fcl_freight_commodity_cluster.execute()

    return {'id' : request['id']}
