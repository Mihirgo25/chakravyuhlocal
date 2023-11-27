from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from playhouse.postgres_ext import ServerSide
from fastapi.encoders import jsonable_encoder
import datetime


def haulage_migration():
    haulage_freight = HaulageFreightRate.select().where(
        HaulageFreightRate.source == 'predicted',
        HaulageFreightRate.transport_modes_keyword == 'trailer',
        ~HaulageFreightRate.rate_not_available_entry,
        HaulageFreightRate.validity_end >= datetime.datetime.now().date()
    )
    for freight in ServerSide(haulage_freight):
        line_items = jsonable_encoder(freight.line_items)
        new_line_items = []
        bas_currency = 'INR'
        fsc_charge = {}

        for line_item in line_items:
            if line_item['code']!='FSC':
                new_line_items.append(line_item)
            else:
                fsc_charge = line_item
            if line_item['code'] == 'BAS':
                bas_currency = line_item['currency']
            
            if fsc_charge:
                fsc_charge['currency'] = bas_currency
                new_line_items.append(fsc_charge)
        
        freight.line_items = new_line_items
        freight.save()

        
