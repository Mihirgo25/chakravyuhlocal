from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from fastapi import HTTPException
from database.db_session import db
from datetime import datetime
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit

def create_audit(request):

    data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id','id'] and not value == None}

    FclServiceAudit.create(
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = data,
        object_id = request['id'],
        object_type = 'FclFreightCommodityCluster'
    )

def update_fcl_freight_commodity_cluster(request):
    object_type = 'Fcl_Freight_Commodity_Cluster'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
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
    create_audit(request)

    return {'id' : request['id']}
