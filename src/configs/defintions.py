import os
import yaml

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
FCL_FREIGHT_CHARGES = os.path.join(ROOT_DIR, "charges", "fcl_freight_charges.yml")
FCL_FREIGHT_LOCAL_CHARGES = os.path.join(ROOT_DIR, "charges", "fcl_freight_local_charges.yml")
FCL_FREIGHT_CURRENCIES = os.path.join(ROOT_DIR, "libs", "currencies.yml")
FCL_FREIGHT_SEASONAL_CHARGES = os.path.join(ROOT_DIR, "charges", "fcl_freight_seasonal_charges.yml")