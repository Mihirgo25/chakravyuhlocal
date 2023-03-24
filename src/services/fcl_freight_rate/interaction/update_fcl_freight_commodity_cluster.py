from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from fastapi import HTTPException
from database.db_session import db
from datetime import datetime

def update_fcl_freight_commodity_cluster(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            raise e

def execute_transaction_code(request):
    if type(request) != dict:
        request = request.dict(exclude_none = False)

    update_params = {key: value for key, value in request.items() if key in ['name', 'commodities', 'status']}
    update_params['updated_at'] = datetime.now()

    fcl_freight_commodity_cluster = FclFreightCommodityCluster.update(update_params).where(FclFreightCommodityCluster.id == request['id'])

    if fcl_freight_commodity_cluster.execute() == 0:
        raise HTTPException(status_code=422, detail="Commodity Cluster not updated")

    return {'id' : request['id']}
