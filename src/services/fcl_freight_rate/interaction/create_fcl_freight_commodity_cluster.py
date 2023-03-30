from services.fcl_freight_rate.models.fcl_freight_commodity_cluster import FclFreightCommodityCluster
from fastapi import HTTPException
from database.db_session import db
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit

def create_audit(request, freight_commodity_cluster_id):

    data = {key:str(value) for key, value in request.items() if key not in ['performed_by_id'] and not value == None}

    FclServiceAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = data,
        object_id = freight_commodity_cluster_id,
        object_type = 'FclFreightCommodityCluster'
    )

def create_fcl_freight_commodity_cluster(request):
    object_type = 'Fcl_Freight_Commodity_Cluster'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
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
        raise HTTPException(status_code=500, detail="Commodity Cluster not saved")
    create_audit(request,fcl_freight_commodity_cluster.id)

    return {'id' : fcl_freight_commodity_cluster.id}
