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
from configs.global_constants import BATCH_SIZE

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
            raise HTTPException(status_code=400, detail="Invalid action Name")

    def validate_update_freight_rate_data(self):
        data = self.data
        if not data["new_end_date"]:
            raise HTTPException(status_code=400, detail="new end date is invalid")

        if not data["new_start_date"]:
            raise HTTPException(status_code=400, detail="new start date is invalid")

        if (
            datetime.fromisoformat(data["new_end_date"]).date()
            > (datetime.now() + timedelta(days=120)).date()
        ):
            raise HTTPException(
                status_code=400,
                detail="new end date can not be greater than 120 days from current date",
            )

        if (
            datetime.fromisoformat(data["new_start_date"]).date()
            < (datetime.now() - timedelta(days=15)).date()
        ):
            raise HTTPException(
                status_code=400,
                detail="new start date can not be less than 15 days from current date",
            )

        if (
            datetime.fromisoformat(data["new_end_date"]).date()
            <= datetime.fromisoformat(data["new_start_date"]).date()
        ):
            raise HTTPException(
                status_code=400,
                detail="new end date can not be lesser than or equal to start validity",
            )

    def validate_add_freight_rate_markup_data(self):
        data = self.data
        if float(data["markup"]) == 0:
            raise HTTPException(status_code=400, detail="markup cannot be 0")

        markup_types = ["net", "percent"]

        if data["markup_type"] not in markup_types:
            raise HTTPException(status_code=400, detail="markup_type is invalid")

        if str(data["markup_type"]).lower() == "percent":
            return

        currencies = AIR_FREIGHT_CURRENCIES

        if data["markup_currency"] not in currencies:
            raise HTTPException(
                status_code=400, detail="markup_currency is invalid"
            )

    def validate_add_min_price_markup_data(self):
        data = self.data

        if float(data["markup"]) == 0:
            raise HTTPException(status_code=400, detail="markup cannot be 0")

        markup_types = ["net", "percent"]

        if data["markup_type"] not in markup_types:
            raise HTTPException(status_code=400, detail="markup_type is invalid")

        if str(data["markup_type"]).lower() == "percent":
            return

        currencies = AIR_FREIGHT_CURRENCIES

        if data["markup_currency"] not in currencies:
            raise HTTPException(status_code=400, detail="currency is invalid")

    def validate_delete_freight_rate_data(self):
        return

    def validate_add_local_rate_markup_data(self):
        data = self.data

        if float(data["markup"]) == 0 and float(data["min_price_markup"]) == 0:
            raise HTTPException(
                status_code=400, detail="markup and min_price_markup both cannot be 0"
            )

        markup_types = ["net", "percent"]

        if data["markup_type"] not in markup_types:
            raise HTTPException(status_code=400, detail="markup_type is invalid")

        if data["min_price_markup_type"] not in markup_types:
            raise HTTPException(
                status_code=400, detail="min_price_markup_type is invalid"
            )

        charge_codes = AIR_FREIGHT_LOCAL_CHARGES

        if data["line_item_code"] not in charge_codes:
            raise HTTPException(status_code=400, detail="line_item_code is invalid")

        currencies = AIR_FREIGHT_CURRENCIES

        if (
            str(data["markup_type"]).lower() == "net"
            and data["markup_currency"] not in currencies
        ):
            raise HTTPException(status_code=400, detail="markup currency is invalid")

        if (
            str(data["min_price_markup_type"]).lower() == "net"
            and data["min_price_markup_currency"] not in currencies
        ):
            raise HTTPException(
                status_code=400, detail="min price markup currency is invalid"
            )

    def validate_update_storage_free_limit_data(self):
        data = self.data

        if int(data["free_limit"]) < 0:
            raise HTTPException(
                status_code=400, detail="free_limit cannot be less than  0"
            )

        slabs = sorted(
            data.get("slabs", []), key=lambda slab: slab.get("lower_limit", 0)
        )

        if any(
            slab.get("upper_limit", 0) <= slab.get("lower_limit", 0) for slab in slabs
        ):
            raise HTTPException(status_code=400, detail="slabs is invalid")

        if len(slabs) > 0 and (int(slabs[0]["lower_limit"]) <= int(data["free_limit"])):
            raise HTTPException(
                status_code=400,
                detail="slabs lower limit should be greater than free limit",
            )

        if any(
            index > 0
            and slab.get("lower_limit", 0) <= slabs[index - 1].get("upper_limit", 0)
            for index, slab in enumerate(slabs)
        ):
            raise HTTPException(status_code=400, detail="slabs is invalid")

        slab_currency = [slab["currency"] for slab in slabs]
        currencies = AIR_FREIGHT_CURRENCIES

        if len(list(set(slab_currency).difference(currencies))) > 0:
            raise HTTPException(status_code=400, detail="slab currency is invalid")

    def perform_batch_wise_delete_freight_rate_action(self,count,batches_query,total_count):
        data = self.data
        freight_rates = jsonable_encoder(list(batches_query.dicts()))
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
            delete_air_freight_rate(
                {
                    "id": freight["id"],
                    "performed_by_id": self.performed_by_id,
                    "validity_id": freight['validity']['id'],
                    "bulk_operation_id": self.id,
                }
            )

            self.progress = (count * 100.0) / int(total_count)
            self.save()
        return count
    
    def perform_delete_freight_rate_action(self):
        data = self.data
        filters  = data['filters']

        query = list_air_freight_rates(filters=filters,return_query=True)['list']
        total_count = query.count()
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
        for freight in freight_rates:
            print(freight)
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
                

            slabs = freight['validity']["weight_slabs"]
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
                    "validity_id": freight['validity']["id"],
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

        query = list_air_freight_rates(filters=filters,return_query=True)['list']
        total_count = query.count()
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


    def perform_add_min_price_markup_action(self,procured_by_id,sourced_by_id):
        data = self.data
        filters = (data["filters"] or {}) | (
            {"service_provider_id": self.service_provider_id}
        )

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        air_freight_rates = list_air_freight_rates(
            filters=filters, return_query=True, page_limit=page_limit
        )["list"]

        total_count = len(air_freight_rates)
        count = 0

        for freight in air_freight_rates:
            count += 1

            if AirFreightRateAudit.select().where(
                AirFreightRateAudit.bulk_operation_id == self.id,
                AirFreightRateAudit.object_id == freight["id"],
            ):
                self.progress = (count * 100.0) / int(total_count)
                self.save()
                continue

            freight["min_price"] = float(freight["min_price"])
            if data["markup_type"].lower() == "percent":
                markup = float(data["markup"] * freight["min_price"]) / 100
            else:
                markup = data["markup"]

            if data["markup_type"].lower() == "net":
                if data["markup_currency"] != freight["currency"]:
                    markup = common.get_money_exchange_for_fcl(
                        {
                            "from_currency": data["markup_currency"],
                            "to_currency": freight["currency"],
                            "price": markup,
                        }
                    )["price"]

            freight["min_price"] = freight["min_price"] + markup
            if freight["min_price"] < 0:
                freight["min_price"] = 0
            freight["min_price"] = round(freight["min_price"], 4)

            update_air_freight_rate(
                {
                    "id": freight["air_freight_rate_id"],
                    "currency": freight["currency"],
                    "min_price": freight["min_price"],
                    "performed_by_id": self.performed_by_id,
                    "bulk_operation_id": self.id,
                    "weight_slabs": freight["weight_slabs"],
                    "procured_by_id": procured_by_id,
                    "sourced_by_id": sourced_by_id,
                }
            )
            self.progress = (count * 100.0) / int(total_count)
            self.save()

    def perform_add_local_rate_markup_action(self,sourced_by_id,procured_by_id):
        data = self.data
        if cogo_entity_id == "None":
            cogo_entity_id = None
        filters = (data["filters"] or {}) | (
            {"service_provider_id": self.service_provider_id}
        )

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        local_rates = list_air_freight_rate_locals(
            filters=filters, return_query=True, page_limit=page_limit
        )["list"]
        total_count = len(local_rates)
        count = 0

        for local in local_rates:
            count += 1

            if AirFreightRateAudit.get_or_none(
                "bulk_operation_id" == self.id, object_id=local["id"]
            ):
                self.progress = (count * 100.0) / int(total_count)
                self.save()
                continue

            line_items = [
                t
                for t in local["data"]["line_items"]
                if t["code"] == data["line_item_code"]
            ]
            if not line_items:
                self.progress = (count * 100.0) / int(total_count)
                self.save()

            local["data"]["line_items"] = local["data"]["line_items"] - line_items

            for line_item in line_items:
                if data["markup_type"].lower() == "percent":
                    markup = float(data["markup"] * line_item["price"]) / 100
                else:
                    markup = data["markup"]

                if data["markup_type"].lower() == "net":
                    markup = common.get_money_exchange_for_fcl(
                        {
                            "from_currency": data["markup_currency"],
                            "to_currency": line_item["currency"],
                            "price": markup,
                        }
                    )["price"]

                line_item["price"] = line_item["price"] + markup

                if line_item["price"] < 0:
                    line_item["price"] = 0

                if data["min_price_markup_type"].lower() == "percent":
                    markup = (
                        float(data["min_price_markup_type"] * line_item["min_price"])
                        / 100
                    )
                else:
                    markup = data["min_price_markup"]

                if data["min_price_markup_type"].lower() == "net":
                    markup = common.get_money_exchange_for_fcl(
                        {
                            "from_currency": data["min_price_markup_currency"],
                            "to_currency": line_item["currency"],
                            "price": markup,
                        }
                    )["price"]

                line_item["price"] = line_item["price"] + markup

                if line_item["min_price"] < 0:
                    line_item["min_price"] = 0

                for slab in line_item["slabs"]:
                    if data["markup_type"].lower() == "percent":
                        markup = float(data["markup"] * slab["price"]) / 100
                    else:
                        markup = data["markup"]

                    if data["markup_type"].lower() == "net":
                        markup = common.get_money_exchange_for_air(
                            {
                                "from_currency": data["markup_currency"],
                                "to_currency": line_item["currency"],
                                "price": markup,
                            }
                        )["price"]

                    slab["price"] = slab["price"] + markup
                    if slab["price"] < 0:
                        slab["price"] = 0

                local["data"]["line_items"].append(line_item)

                update_air_freight_rate_local(
                    {
                        "id": local["id"],
                        "performed_by_id": self.performed_by_id,
                        "sourced_by_id": sourced_by_id,
                        "procured_by_id": procured_by_id,
                        "bulk_operation_id": self.id,
                        "data": local["data"],
                    }
                )

                self.progress = (count * 100.0) / int(total_count)
                self.save()

    def perform_update_storage_free_limit_action(self,sourced_by_id,procured_by_id):
        data = self.data
        filters = data["filters"] | ({"service_provider_id": self.service_provider_id})

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        storage_rates = list_air_freight_storage_rates(
            filters=filters, return_query=True, page_limit=page_limit
        )["list"]
        storage_rates = list(storage_rates.dicts())

        total_count = len(storage_rates)
        count = 0
        for storage in storage_rates:
            count += 1

            if AirFreightRateAudit.get_or_none(
                bulk_operation_id=self.id, object_id=storage["air_freight_rate_id"]
            ):
                self.progress = (count * 100.0) / int(total_count)
                self.save()
                continue

            update_air_freight_storage_rate({
                'id': storage["air_freight_rate_id"],
                'performed_by_id': self.performed_by_id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id,
                'bulk_operation_id': self.id,
                'slabs': data['slabs'],
                'free_limit': data['free_limit']
            })

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
                    "validity_id": freight['validity']['id'],
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
