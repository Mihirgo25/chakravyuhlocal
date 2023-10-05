import os
from micro_services.client import common 
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "..")) 

class Charges:
    def __init__(self,key) -> None:
        self.key = key
    
    def get(self):
        return common.get_charge(self.key)
   
        
FCL_FREIGHT_CHARGES = Charges('fcl_freight_charges')
FCL_FREIGHT_LOCAL_CHARGES = Charges('fcl_freight_local_charges')
FCL_FREIGHT_CURRENCIES = Charges('currencies')
FCL_FREIGHT_SEASONAL_CHARGES = Charges('fcl_freight_seasonal_charges')
FCL_CFS_CHARGES  = Charges('fcl_cfs_charges')
FCL_CUSTOMS_CHARGES = Charges('fcl_customs_charges')
AIR_FREIGHT_CHARGES=Charges('air_freight_charges')
AIR_FREIGHT_LOCAL_CHARGES=Charges('air_freight_local_charges')
AIR_FREIGHT_SURCHARGES= Charges('air_freight_surcharges')
AIR_FREIGHT_WAREHOUSE_CHARGES=Charges('air_freight_warehouse_charges')
AIR_FREIGHT_CURRENCIES= Charges('currencies')
HAULAGE_FREIGHT_CHARGES = Charges('haulage_freight_charges')
AIR_CUSTOMS_CHARGES = Charges('air_customs_charges')
