from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from services.conditional_line_items.models.conditional_line_items_audit import ConditionalLineItemAudit
from datetime import datetime

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class ConditionalLineItems(BaseModel):
    id = BigAutoField(primary_key=True)
    port_id = UUIDField(index=True, null=True)
    main_port_id = UUIDField(null=True)
    country_id = UUIDField(index=True, null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    charge_code = CharField(index=True, null=True)
    data = BinaryJSONField(null = True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    commodity = CharField(null=True)
    status = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.now()
      return super(ConditionalLineItems, self).save(*args, **kwargs)

    class Meta:
        table_name = 'conditional_line_items'
    
    def create_audit(self, param):
        audit = ConditionalLineItemAudit.create(**param)
        return audit