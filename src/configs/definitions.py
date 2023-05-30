import os
import yaml

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

class LoadYmls():
    FCL_FREIGHT_CHARGES = None
    FCL_FREIGHT_LOCAL_CHARGES = None
    FCL_FREIGHT_CURRENCIES = None
    FCL_FREIGHT_SEASONAL_CHARGES = None
    FCL_CFS_CHARGES  = None
    
    def __init__(self):
        self.FCL_FREIGHT_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_freight_charges.yml"))
        self.FCL_FREIGHT_LOCAL_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_freight_local_charges.yml"))
        self.FCL_FREIGHT_CURRENCIES = self.load_ymls(os.path.join(ROOT_DIR, "libs", "currencies.yml"))
        self.FCL_FREIGHT_SEASONAL_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_freight_seasonal_charges.yml"))
        self.FCL_CFS_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_cfs_charges.yml"))
        self.FCL_CUSTOMS_CHARGES = self.load_ymls(os.path.join(ROOT_DIR, "charges", "fcl_customs_charges.yml"))

        
    def load_ymls(self, file):
        with open(file, 'r') as f:
            data = yaml.safe_load(f)
        return data
    
yml_obj = LoadYmls() 

FCL_FREIGHT_CHARGES = yml_obj.FCL_FREIGHT_CHARGES
FCL_FREIGHT_LOCAL_CHARGES = yml_obj.FCL_FREIGHT_LOCAL_CHARGES
FCL_FREIGHT_CURRENCIES = yml_obj.FCL_FREIGHT_CURRENCIES
FCL_FREIGHT_SEASONAL_CHARGES = yml_obj.FCL_FREIGHT_SEASONAL_CHARGES 
FCL_CFS_CHARGES  = yml_obj.FCL_CFS_CHARGES 
FCL_CUSTOMS_CHARGES = yml_obj.FCL_CUSTOMS_CHARGES
    