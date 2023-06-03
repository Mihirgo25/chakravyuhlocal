from datetime import datetime
from fastapi import HTTPException
from database.db_session import db 

def execute(request):
    with db.atomic():
        return create_air_freight_warehouse_rate(request)
    
def create_air_freight_warehouse_rate(request):
    object=find_object(request)

def find_object(request):
    return 

