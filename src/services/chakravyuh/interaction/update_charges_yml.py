from libs.get_charges_yml import get_charge_from_rd, set_charge_to_rd,get_charge_key
from micro_services.client import common 
from database.db_session import rd


def update_charges_yml(serviceChargeType):
   rd.delete(get_charge_key(serviceChargeType))
   temp=common.get_charge(serviceChargeType)
   return "Charge data deleted successfully"