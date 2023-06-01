from datetime import datetime
from database.db_session import db  
from fastapi import HTTPException

def create_air_freight_rate_bulk_operation(request):
    action_name=[key for key in request if key not in ['performed_by_id']][0]
    data=request[action_name]

    