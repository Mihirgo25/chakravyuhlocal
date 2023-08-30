from database.db_session import db
from peewee import *
from playhouse.postgres_ext import *
from micro_services.client import *
from fastapi import HTTPException
from datetime import datetime, timedelta
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.air_freight_rate.interactions.delete_air_freight_rate import delete_air_freight_rate
from services.air_freight_rate.interactions.delete_air_freight_rate_local import delete_air_freight_rate_local
from services.air_freight_rate.interactions.update_air_freight_rate_local import update_air_freight_rate_local
from services.air_freight_rate.interactions.update_air_freight_rate_markup import update_air_freight_rate_markup
from services.air_freight_rate.interactions.update_air_freight_rate import update_air_freight_rate
from services.air_freight_rate.interactions.list_air_freight_rates import list_air_freight_rates
from services.air_freight_rate.interactions.list_air_freight_rate_surcharges import list_air_freight_rate_surcharges
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.interactions.list_air_freight_rate_locals import list_air_freight_rate_locals
from services.air_freight_rate.models.air_freight_rate_audit import AirFreightRateAudit
from services.air_freight_rate.interactions.update_air_freight_storage_rate import update_air_freight_storage_rate
from configs.definitions import AIR_FREIGHT_CURRENCIES,AIR_FREIGHT_LOCAL_CHARGES
from services.air_freight_rate.interactions.list_air_freight_storage_rates import list_air_freight_storage_rates
from services.air_freight_rate.interactions.delete_air_freight_rate_surcharge import delete_air_freight_rate_surcharge
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from fastapi.encoders import jsonable_encoder
from services.fcl_freight_rate.helpers.fcl_freight_rate_bulk_operation_helpers import get_rate_sheet_id

BATCH_SIZE = 1000

ACTION_NAMES = [
    "update_freight_rate",
    "delete_freight_rate",
    "add_freight_rate_markup",
    "delete_freight_rate_surcharge",
    "delete_freight_rate_local",
]


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateBulkOperation(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    progress = IntegerField(null=True)
    action_name = CharField(null=True)
    performed_by_id = UUIDField(null=True,index=True)
    data = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.now)
    created_at = DateTimeField(default=datetime.now)
    service_provider_id = UUIDField(null=True)

    class Meta:
        table_name = "air_freight_rate_bulk_operations"

    def validate_action_name(self):
        if self.action_name not in ACTION_NAMES:
            raise HTTPException(status_code=400, detail="Invalid Action Name")

    def validate_update_freight_rate_data(self):
        data = self.data
        if not data["new_end_date"]:
            raise HTTPException(status_code=400, detail="New End Date Is Invalid")

        if not data["new_start_date"]:
            raise HTTPException(status_code=400, detail="New Start Date Is Invalid")

        if (
            datetime.fromisoformat(data["new_end_date"]).date()
            > (datetime.now() + timedelta(days=120)).date()
        ):
            raise HTTPException(
                status_code=400,
                detail="New End Date Cannot Be Greater Than 120 Days From Current Date",
            )

        if (
            datetime.fromisoformat(data["new_start_date"]).date()
            < (datetime.now() - timedelta(days=15)).date()
        ):
            raise HTTPException(
                status_code=400,
                detail="New Start Date Cannot Be Less Than 15 Days From Current Date",
            )

        if (
            datetime.fromisoformat(data["new_end_date"]).date()
            <= datetime.fromisoformat(data["new_start_date"]).date()
        ):
            raise HTTPException(
                status_code=400,
                detail="New End Date Cannot Be Lesser Than Or Equal To Start Validity",
            )

    def validate_add_freight_rate_markup_data(self):
        data = self.data
        if float(data["markup"]) == 0:
            raise HTTPException(status_code=400, detail="Markup Cannot Be 0")

        markup_types = ["net", "percent"]

        if data["markup_type"] not in markup_types:
            raise HTTPException(status_code=400, detail="Markup Type Is Invalid")

        if str(data["markup_type"]).lower() == "percent":
            return

        currencies = AIR_FREIGHT_CURRENCIES

        if data["markup_currency"] not in currencies:
            raise HTTPException(
                status_code=400, detail="Markup Currency Is Invalid"
            )
               
        if data.get('rates_greater_than_price')!=None and data.get('rates_greater_than_price')!=None and data['rates_greater_than_price'] > data['rates_less_than_price']:
            raise HTTPException(status_code=400, detail='Greater than price cannot be greater than Less than price')
        
        if data.get('rate_sheet_serial_id'):
            rate_sheet_id = get_rate_sheet_id(data.get('rate_sheet_serial_id'))
            if not rate_sheet_id:
                raise HTTPException(status_code=400, detail='Invalid Rate sheet serial id') 
            

    def validate_delete_freight_rate_data(self):
        data = self.data
        if data['validity_end'] < data['validity_start']:
            raise HTTPException(status_code=400, detail='validity_end cannot be less than validity start')
        
        if data.get('rates_greater_than_price')!=None and data.get('rates_greater_than_price')!=None and data['rates_greater_than_price'] > data['rates_less_than_price']:
            raise HTTPException(status_code=400, detail='Greater than price cannot be greater than Less than price')
        
        if data.get('rate_sheet_serial_id'):
            rate_sheet_id = get_rate_sheet_id(data.get('rate_sheet_serial_id'))
            if not rate_sheet_id:
                raise HTTPException(status_code=400, detail='Invalid Rate sheet serial id') 
        
        data['validity_start'] = data['validity_start'].date()
        data['validity_end'] = data['validity_end'].date()
        return

    def validate_add_local_rate_markup_data(self):
        data = self.data

        if float(data["markup"]) == 0 and float(data["min_price_markup"]) == 0:
            raise HTTPException(
                status_code=400, detail="Markup And Min Price Markup Both Cannot Be 0"
            )

        markup_types = ["net", "percent"]

        if data["markup_type"] not in markup_types:
            raise HTTPException(status_code=400, detail="Markup Type Is Invalid")

        if data["min_price_markup_type"] not in markup_types:
            raise HTTPException(
                status_code=400, detail="Min Price Markup Type Is Invalid"
            )

        charge_codes = AIR_FREIGHT_LOCAL_CHARGES

        if data["line_item_code"] not in charge_codes:
            raise HTTPException(status_code=400, detail="Line Item Code Is Invalid")

        currencies = AIR_FREIGHT_CURRENCIES

        if (
            str(data["markup_type"]).lower() == "net"
            and data["markup_currency"] not in currencies
        ):
            raise HTTPException(status_code=400, detail="Markup Currency Is Invalid")

        if (
            str(data["min_price_markup_type"]).lower() == "net"
            and data["min_price_markup_currency"] not in currencies
        ):
            raise HTTPException(
                status_code=400, detail="Min Price Markup Currency Is Invalid"
            )

    def perform_batch_wise_delete_freight_rate_action(self,count,batches_query,total_count):
        data = self.data
        freight_rates = jsonable_encoder(list(batches_query.dicts()))
        weight_slabs = data['weight_slabs']
        for freight in freight_rates:
            count += 1
            if AirFreightRateAudit.select().where(
                AirFreightRateAudit.bulk_operation_id == self.id,
                AirFreightRateAudit.object_id == freight["id"],
                AirFreightRateAudit.validity_id == freight['validity']['id']
            ).execute():
                self.progress = (count * 100.0) / int(total_count)
                self.save()
                continue
            new_weight_slabs = []
            slabs = freight['validity']["weight_slabs"]
            slabs = get_weight_slabs(freight['weight_slabs'],weight_slabs,data)

            if not new_weight_slabs:
                delete_air_freight_rate(
                    {
                        "id": freight["id"],
                        "performed_by_id": self.performed_by_id,
                        "validity_id": freight['validity']['id'],
                        "bulk_operation_id": self.id,
                    }
                )
            else:
                update_air_freight_rate(
                {
                    "id": freight["id"],
                    "validity_id": freight['validity']["id"],
                    "performed_by_id": self.performed_by_id,
                    "bulk_operation_id": self.id,
                    "min_price": freight['validity']["min_price"],
                    "currency": freight['validity']["currency"],
                    "weight_slabs": new_weight_slabs,
                }
            )

            self.progress = (count * 100.0) / int(total_count)
            self.save()
        return count
    
    def perform_delete_freight_rate_action(self):
        data = self.data
        filters  = data['filters']
        rate_sheet_id=get_rate_sheet_id(data.get('rate_sheet_serial_id'))
        rate_ids = []
        rate_ids += get_relevant_rate_ids_from_audits_for_rate_sheet(rate_sheet_id)
        if rate_ids:
            if isinstance(filters.get('id'), list):
                rate_ids += filters['id']
            elif filters.get('id'):
                rate_ids += [filters['id']]
            filters['id'] = rate_ids
        query = list_air_freight_rates(filters=filters,return_query=True)['list']
        total_count = query.count()
        if total_count ==0:
            self.progress ==100
            self.save()
            return
        count =0
        offset =0
        while count < total_count:
            batches_query = query.offset(offset).limit(BATCH_SIZE)
            if not batches_query.exists():
                break
            count = self.perform_batch_wise_delete_freight_rate_action(count,batches_query,total_count)
            offset = offset + BATCH_SIZE
        self.progress = (count * 100.0) / int(total_count)
        self.save()


    def perform_batch_wise_add_freight_rate_markup_action(self,batches_query, count , total_count):
        freight_rates = jsonable_encoder(list(batches_query.dicts()))
        data = self.data
        weight_slabs = data['weight_slabs']
        for freight in freight_rates:
            count += 1
            if (
                AirFreightRateAudit.select()
                .where(
                    AirFreightRateAudit.bulk_operation_id == self.id,
                    AirFreightRateAudit.object_id == freight["id"],
                    AirFreightRateAudit.validity_id == freight['validity']['id']
                )
                .first()
            ):
                self.progress = (count * 100.0) / int(total_count)
                self.save()
                continue
                

            slabs = get_weight_slabs(freight['weight_slabs'],weight_slabs,data)
            for slab in slabs:
                if data["markup_type"].lower() == "percent":
                    markup = (
                        float(data["markup"] * slab["tariff_price"]) / 100
                    )
                else:
                    markup = data["markup"]

                if data["markup_type"].lower() == "net":
                    if data["markup_currency"] != slab["currency"]:
                        markup = common.get_money_exchange_for_fcl(
                            {
                                "from_currency": data["markup_currency"],
                                "to_currency": slab["currency"],
                                "price": markup,
                            }
                        )["price"]

                slab["tariff_price"] = slab["tariff_price"] + markup
                if slab["tariff_price"] < 0:
                    slab["tariff_price"] = 0
                slab["tariff_price"] = round(slab["tariff_price"], 4)

            update_air_freight_rate(
                {
                    "id": freight["id"],
                    "performed_by_id": self.performed_by_id,
                    "bulk_operation_id": self.id,
                    "min_price": freight['validity']["min_price"],
                    "currency": freight['validity']["currency"],
                    "weight_slabs": slabs,
                }
            )
            self.progress = (count * 100.0) / int(total_count)
            self.save()
        return count

    def perform_add_freight_rate_markup_action(self):
        data = self.data
        filters  = data['filters']
        rate_sheet_id=get_rate_sheet_id(data.get('rate_sheet_serial_id'))
        rate_ids = []
        rate_ids += get_relevant_rate_ids_from_audits_for_rate_sheet(rate_sheet_id)
        if rate_ids:
            if isinstance(filters.get('id'), list):
                rate_ids += filters['id']
            elif filters.get('id'):
                rate_ids += [filters['id']]
            filters['id'] = rate_ids
        query = list_air_freight_rates(filters=filters,return_query=True)['list']
        total_count = query.count()
        if total_count ==0:
            self.progress ==100
            self.save()
            return
        count =0
        offset =0
        while count < total_count:
            batches_query = query.offset(offset).limit(BATCH_SIZE)
            if not batches_query.exists():
                break
            count = self.perform_batch_wise_add_freight_rate_markup_action(batches_query, count,total_count)
            offset = offset + BATCH_SIZE
        self.progress = (count * 100.0) / int(total_count)
        self.save()


    def perform_batch_wise_update_freight_rate_action(self,batches_query, count,total_count):
        freights  = jsonable_encoder(list(batches_query.dicts()))
        data = self.data
        for freight in freights:
            count += 1

            if AirFreightRateAudit.get_or_none(
                bulk_operation_id=self.id, object_id=freight["id"],validity_id = freight['validity']['id']
            ):
                self.progress = (count * 100.0) / int(total_count)
                self.save()
                continue

            update_air_freight_rate_markup(
                {
                    "id": freight["id"],
                    "performed_by_id": self.performed_by_id,
                    "bulk_operation_id": self.id,
                    "validity_start": datetime.strptime(
                        data["new_start_date"], "%Y-%m-%dT%H:%M:%S%z"
                    ),
                    "validity_end": datetime.strptime(
                        data["new_end_date"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                }
            )

            self.progress = (count * 100.0) / int(total_count)
            self.save()
        return count
    
    def perform_update_freight_rate_action(self):
        data = self.data
        filters  = data['filters']
        rate_sheet_id=get_rate_sheet_id(data.get('rate_sheet_serial_id'))
        rate_ids = []
        rate_ids += get_relevant_rate_ids_from_audits_for_rate_sheet(rate_sheet_id)
        if rate_ids:
            if isinstance(filters.get('id'), list):
                rate_ids += filters['id']
            elif filters.get('id'):
                rate_ids += [filters['id']]
            filters['id'] = rate_ids
        query = list_air_freight_rates(filters=filters,return_query=True)['list']
        total_count = query.count()
        count =0
        offset =0
        while count < total_count:
            batches_query = query.offset(offset).limit(BATCH_SIZE)
            if not batches_query.exists():
                break
            count = self.perform_batch_wise_update_freight_rate_action(batches_query, count,total_count)
            offset = offset + BATCH_SIZE
        self.progress = (count * 100.0) / int(total_count)
        self.save()

    def perform_bacth_wise_delete_freight_rate_surcharge_action(self,count,batch_query,total_count):
        freights = jsonable_encoder(list(batch_query.dicts()))
        for freight in freights:
            count += 1

            object = (
                AirServiceAudit.select()
                .where(AirServiceAudit.object_id == freight["id"],
                       AirServiceAudit.bulk_operation_id == self.id
                )
                .first()
            )
            if object:
                self.progress = (count * 100.0) / int(total_count)
                self.save()
                continue

            delete_air_freight_rate_surcharge(
                {
                    "id": freight["id"],
                    "performed_by_id": self.performed_by_id,
                    "bulk_operation_id": self.id,
                }
            )
            self.progress = (count * 100.0) / int(total_count)
            self.save()
        return count
    
    def perform_delete_freight_rate_surcharge_action(self):
        data = self.data
        filters = data['filters']
        query = list_air_freight_rate_surcharges(filters=filters,return_query=True)['list']
        total_count = query.count()
        if total_count == 0:
            self.progress = 100
            self.save()
            return
        count = 0
        offset = 0
        while count < total_count:
            batch_query = query.offset(offset).limit(BATCH_SIZE)
            count = self.perform_bacth_wise_delete_freight_rate_surcharge_action(count,batch_query,total_count)
            offset = offset + BATCH_SIZE
        self.progress = (count * 100.0) / int(total_count)
        self.save()

    def perform_bacth_wise_delete_freight_rate_local_action(self,count,batch_query,total_count):
        freights = jsonable_encoder(list(batch_query.dicts()))
        for freight in freights:
            count += 1

            object = (
                AirServiceAudit.select()
                .where(
                    AirServiceAudit.object_id == freight["id"],
                    AirServiceAudit.bulk_operation_id == self.id
                )
                .first()
            )
            if object:
                self.progress = (count * 100.0) / int(total_count)
                self.save()
                continue

            delete_air_freight_rate_local(
                {
                    "id": freight["id"],
                    "performed_by_id": self.performed_by_id,
                    "bulk_operation_id": self.id,
                }
            )
            self.progress = (count * 100.0) / int(total_count)
            self.save()
        return count
    
    def perform_delete_freight_rate_local_action(self):
        data = self.data
        filters = data['filters']
        query = list_air_freight_rate_locals(filters=filters,return_query=True)['list']
        total_count = query.count()
        if total_count == 0:
            self.progress = 100
            self.save()
            return
        count = 0
        offset = 0
        while count < total_count:
            batch_query = query.offset(offset).limit(BATCH_SIZE)
            count = self.perform_bacth_wise_delete_freight_rate_local_action(count,batch_query,total_count)
            offset = offset + BATCH_SIZE
        self.progress = (count * 100.0) / int(total_count)
        self.save()

    def add_freight_rate_markup_detail(self):
        return

    def add_min_price_markup_detail(self):
        return

    def delete_freight_rate_detail(self):
        return

    def add_local_rate_markup_detail(self):
        return

    def update_storage_free_limit_detail(self):
        return

    def validate_delete_freight_rate_surcharge_data(self):
        return

    def validate_delete_freight_rate_local_data(self):
        return


def create_audit(id):
    AirFreightRateAudit.create(bulk_operation_id=id)

def get_relevant_rate_ids_from_audits_for_rate_sheet(rate_sheet_id):
    if not rate_sheet_id:
        return []

    query = AirFreightRateAudit.select(AirFreightRateAudit.object_id).where((AirFreightRateAudit.rate_sheet_id == rate_sheet_id)) 
    return [str(result['object_id']) for result in list(query.dicts())]

def get_weight_slabs(freight_validity_weight_slabs,weight_slabs_to_effect,data):
    weight_slabs = []
    if len(weight_slabs) ==0:
        weight_slabs = freight_validity_weight_slabs
    else:
        for slab in freight_validity_weight_slabs:
            for weight_slab in weight_slabs_to_effect:
                if slab['lower_limit'] >=weight_slab['lower_limit'] and slab['upper_limit'] <= weight_slab['upper_limit']:
                    weight_slabs.append(weight_slab)
                    break
    
    if data.get('rates_greater_than_price') and data.get('rates_less_than_price'):
        weight_slabs = filter_price_wise(weight_slabs,data)
    return weight_slabs

def filter_price_wise(weight_slabs,data):
    new_weight_slabs = []
    for weight_slab in weight_slabs:
        if weight_slab['currency']!=data['comparison_currency']:
            weight_slab['tariff_price'] = common.get_money_exchange_for_fcl({
                            "from_currency": weight_slab['currency'],
                            "to_currency": data['comparison_currency'],
                            "price": weight_slab['tariff_price'],
                        })['price']
        greater_than = False
        less_than = False
        if not data.get('rates_greater_than_price') or (data.get('rates_greater_than_price') and weight_slab['tariff_price'] >= data['rates_greater_than_price']):
            greater_than = True
        if not data.get('rates_less_than_price') or (data.get('rates_less_than_price') and weight_slab['tariff_price'] <= data['rates_less_than_price']):
            less_than = True

        if greater_than and less_than:
            new_weight_slabs.append(weight_slab)
    return new_weight_slabs
                
            

    


