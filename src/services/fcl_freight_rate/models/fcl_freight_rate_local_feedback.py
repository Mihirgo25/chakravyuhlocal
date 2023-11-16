from peewee import *
from database.db_session import db
from database.rails_db import get_user
from playhouse.postgres_ext import *
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import REQUEST_SOURCES
import datetime
from configs.global_constants import PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID
from micro_services.client import *
from database.rails_db import *
from database.rails_db import get_operators
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateLocalFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    fcl_freight_rate_local_id = UUIDField(null=True,index=True)
    feedback_type = CharField(index=True, null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    booking_params = BinaryJSONField(index=True, null=True)
    cogo_entity_id = UUIDField(index=True,null=True)
    cargo_readiness_date = DateField(null=True)
    closed_by_id = UUIDField(index=True, null=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = ArrayField(field_class=CharField, null=True)
    commodity = CharField(null=True)
    container_size=CharField(null=True)
    container_type=CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(index=True, default=datetime.datetime.now)
    main_port_id = UUIDField(null=True)
    main_port = BinaryJSONField(null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_org = BinaryJSONField(null=True)
    performed_by_type = CharField(null=True)
    port_id = UUIDField(index=True, null=True)
    port = BinaryJSONField(null=True)
    preferred_rate = DoubleField(null=True)
    preferred_rate_currency = CharField(null=True)
    # preferred_shipping_line_ids = ArrayField(field_class=UUIDField, null=True)
    # preferred_shipping_lines = BinaryJSONField(null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_local_feedback_serial_id_seq'::regclass)")])
    shipping_line_id = UUIDField(null=True)
    shipping_line_detail = BinaryJSONField(null=True)
    source = CharField(null=True)
    source_id = UUIDField(index=True, null=True)
    status = CharField(index=True, null=True)
    trade_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    service_provider_id= UUIDField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "fcl_freight_rate_local_feedbacks"

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateLocalFeedback, self).save(*args, **kwargs)