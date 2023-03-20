from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from fastapi import HTTPException
from database.db_session import db


def create_fcl_freight_commodity_cluster(request):
    with db.atomic() as transaction:
        try:
          return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    row = {
        'name' : request['name']
    }

    fcl_freight_commodity_cluster = FclFreightCommodityCluster.select().where(FclFreightCommodityCluster.name == request['name']).first()

    if not fcl_freight_commodity_cluster:
       fcl_freight_commodity_cluster = FclFreightCommodityCluster(**row)

    fcl_freight_commodity_cluster.commodities = request['commodities']
    fcl_freight_commodity_cluster.status = 'active'
    fcl_freight_commodity_cluster.validate_commodity_cluster()

    if not fcl_freight_commodity_cluster.save():
        raise HTTPException(status_code=422, detail="Commodity Cluster not saved")

    return {'id' : fcl_freight_commodity_cluster.id}
