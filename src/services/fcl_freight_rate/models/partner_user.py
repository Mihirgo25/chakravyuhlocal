from peewee import *
from playhouse.postgres_ext import *
from database.db_session import db_rails

class BaseModel(Model):
    class Meta:
        database = db_rails

class PartnerUser(BaseModel):
    all_geo_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    annual_ctc = DoubleField(null=True)
    annual_ctc_currency = CharField(null=True)
    block_access = BooleanField(null=True)
    bookings_threshold = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    created_at = DateTimeField()
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    is_importer_exporter_user = BooleanField(null=True)
    is_service_provider_user = BooleanField(null=True)
    is_signing_authority = BooleanField(null=True)
    lowest_geo_location_id = UUIDField(null=True)
    lowest_geo_location_type = CharField(null=True)
    manager_id = UUIDField(null=True)
    margin_approval_limit = DoubleField(null=True)
    margin_approval_limit_currency = CharField(null=True)
    margin_approval_max_value = DoubleField(null=True)
    office_location_id = UUIDField(null=True)
    partner_id = UUIDField(null=True)
    preferred_languages = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    query_name = CharField(null=True)
    role_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    roles = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    sales_agent_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    serviceable_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    services = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    shipping_line_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    status = CharField(null=True)
    updated_at = DateTimeField()
    user_id = UUIDField(null=True)
    zone_id = UUIDField(null=True)

    class Meta:
        table_name = 'partner_users'
        indexes = (
            (('partner_id', 'status'), False),
        )