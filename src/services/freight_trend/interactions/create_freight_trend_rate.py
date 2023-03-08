
from database.db_session import db
from services.freight_trend.models.freight_trend_rate import FreightTrendRate
from services.freight_trend.models.freight_trend_audit import FreightTrendAudit
def create_freight_trend_rate(origin_port_id,destination_port_id,commodity,price,currency,validity_start,validity_end,volume,organization_id,performed_by_id):
    with db.atomic as transaction:
        try:
            return execute_transaction_code(origin_port_id,destination_port_id,commodity,price,currency,validity_start,validity_end,volume,organization_id,performed_by_id)
        except:
            transaction.rollback()
            return "Creation Failed"

def execute_transaction_code(origin_port_id,destination_port_id,commodity,price,currency,validity_start,validity_end,volume,organization_id,performed_by_id):
    data = {
        "origin_port_id":origin_port_id,
        "destination_port_id":destination_port_id,
        "commodity":commodity,
        'price':price,
        'currency':currency,
        'validity_start':validity_start,
        'validity_end':validity_end,
        'volume':volume,
        'organization_id':organization_id
        }
    freight_trend_rates=FreightTrendRate(**data)

    if not freight_trend_rates.save():
        raise "ERROR"

    
    
    FreightTrendAudit.create(action_name='create',performed_by_id=performed_by_id,data=data)

    return {'id':freight_trend_rates.id}
    


    

    

