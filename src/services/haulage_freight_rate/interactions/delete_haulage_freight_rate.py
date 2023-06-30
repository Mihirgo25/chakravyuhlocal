from services.haulage_freight_rate.models.haulage_freight_rate import *
from services.haulage_freight_rate.models.haulage_freight_rate_audits import HaulageFreightRateAudit
from fastapi import HTTPException
from services.haulage_freight_rate.interactions.update_haulage_freight_rate_platform_prices import update_haulage_freight_rate_platform_prices
from datetime import datetime
def delete_haulage_freight_rate(request):
    with db.atomic():
        return () #execute_transaction_code(request)

