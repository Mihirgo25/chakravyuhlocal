from configs.yml_definitions import FCL_FREIGHT_CHARGES,FCL_FREIGHT_LOCAL_CHARGES,FCL_FREIGHT_CURRENCIES,FCL_FREIGHT_SEASONAL_CHARGES,FCL_CFS_CHARGES,FCL_CUSTOMS_CHARGES,AIR_FREIGHT_CHARGES,AIR_FREIGHT_LOCAL_CHARGES,AIR_FREIGHT_SURCHARGES,AIR_FREIGHT_WAREHOUSE_CHARGES,AIR_FREIGHT_CURRENCIES,HAULAGE_FREIGHT_CHARGES

                                    
def get_charge_fallback(charge_name):
    
    CHARGE_YML_MAP = {
    "fcl_freight_charges": FCL_FREIGHT_CHARGES,
    "fcl_freight_local_charges": FCL_FREIGHT_LOCAL_CHARGES,
    "fcl_freight_currencies": FCL_FREIGHT_CURRENCIES,
    "fcl_freight_seasonal_charges": FCL_FREIGHT_SEASONAL_CHARGES,
    "fcl_cfs_charges": FCL_CFS_CHARGES,
    "fcl_customs_charges": FCL_CUSTOMS_CHARGES,
    "air_freight_charges": AIR_FREIGHT_CHARGES,
    "air_freight_local_charges": AIR_FREIGHT_LOCAL_CHARGES,
    "air_freight_surcharges": AIR_FREIGHT_SURCHARGES,
    "air_freight_warehouse_charges": AIR_FREIGHT_WAREHOUSE_CHARGES,
    "air_freight_currencies": AIR_FREIGHT_CURRENCIES,
    "haulage_freight_charges": HAULAGE_FREIGHT_CHARGES,
}

    return CHARGE_YML_MAP.get(charge_name, None)
