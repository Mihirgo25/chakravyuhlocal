
from database.db_session import db 
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
import time
def update():

    count =1
    freights = FclFreightRate.select().where(FclFreightRate.origin_port_id == 'eb187b38-51b2-4a5e-9f3c-978033ca1ddf')
    for freight in freights:
        count+=1
        start = time.time()
        print("1",time.time()-start)
        start = time.time()
        freight.set_locations()
        print("2",time.time()-start)
        start = time.time()
        freight.set_origin_location_ids()
        print("3",time.time()-start)
        start = time.time()
        freight.set_destination_location_ids()
        print("4",time.time()-start)
        start = time.time()
        get_multiple_service_objects(freight)
        print("5",time.time()-start)
        print("******************")

            
    