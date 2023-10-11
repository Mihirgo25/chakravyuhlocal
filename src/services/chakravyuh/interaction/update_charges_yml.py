from libs.get_charges_yml import get_charge_key
from micro_services.client import common 
from database.db_session import rd


def update_charges_yml(serviceChargeType):
   
   rd.delete(get_charge_key(serviceChargeType))
   return "Charge data deleted successfully"