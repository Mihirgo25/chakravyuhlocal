from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *
from micro_services.client import maps


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FclFreightRateLocalJob(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    port_id = UUIDField(index=True, null=True)
    port = BinaryJSONField(index=True, null=True)
    main_port_id = UUIDField(index=True, null=True)
    main_port = BinaryJSONField(index=True, null=True)
    terminal_id = UUIDField(index=True, null=True)
    terminal = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(null=True, index=True)
    shipping_line = BinaryJSONField(null=True)
    service_provider_id = UUIDField(null=True, index=True)
    service_provider = BinaryJSONField(null=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    commodity = CharField(null=True, index=True)
    trade_type = CharField(null=True)
    sources = ArrayField(
        constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True
    )
    user_id = UUIDField(index=True, null=True)
    assigned_to = BinaryJSONField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    status = CharField(index=True, null=True)
    closed_by_id = UUIDField(null=True, index=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = TextField(null=True)
    rate_type = TextField(null=True)
    init_key = TextField(index=True, null=True)
    is_visible = BooleanField(default=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    serial_id = BigIntegerField(
        constraints=[
            SQL("DEFAULT nextval('fcl_freight_rate_local_jobs_serial_id_seq')")
        ],
    )
    search_source = TextField(null=True, index=True)

    class Meta:
        table_name = "fcl_freight_rate_local_jobs"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclFreightRateLocalJob, self).save(*args, **kwargs)

    def set_terminal(self):
        if self.terminal:
            return

        if not self.terminal_id:
            return

        location_ids = [str(self.terminal_id)]

        terminals = maps.list_locations({"filters": {"id": location_ids}})["list"]
        for terminal in terminals:
            if str(terminal.get("id")) == str(self.terminal_id):
                self.terminal = terminal

    def set_shipping_line(self):
        if self.shipping_line or not self.shipping_line_id:
            return
        shipping_line = get_operators(id=self.shipping_line_id)
        if len(shipping_line) != 0:
            shipping_line[0]["id"] = str(shipping_line[0]["id"])
            self.shipping_line = {
                key: value
                for key, value in shipping_line[0].items()
                if key in ["id", "business_name", "short_name", "logo_url"]
            }

    def set_port(self):
        if self.port:
            return

        if not self.port_id:
            return

        location_ids = [str(self.port_id)]
        if self.main_port_id:
            location_ids.append(str(self.main_port_id))
        ports = maps.list_locations({"filters": {"id": location_ids}})["list"]
        for port in ports:
            self.main_port = port
