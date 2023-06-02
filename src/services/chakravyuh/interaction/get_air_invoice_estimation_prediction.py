from services.chakravyuh.setters.air_freight import AirFreightVyuh as AirFreightVyuhSetters
from database.rails_db import get_invoices

def invoice_rates_updation():

    freight_rates = get_invoices()

    for freight_rate in freight_rates:
        setter = AirFreightVyuhSetters(freight_rate)
        setter.set_dynamic_pricing()
        




    


