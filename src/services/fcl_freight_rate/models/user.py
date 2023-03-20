from peewee import *
from playhouse.postgres_ext import *
from database.db_session import db_rails

class BaseModel(Model):
    class Meta:
        database = db_rails

class User(BaseModel):
    alert_preferences = BinaryJSONField(null=True)
    alternate_mobile_number_eformats = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, index=True, null=True)
    alternate_mobile_numbers = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    birth_date = DateField(index=True, null=True)
    created_at = DateTimeField()
    email = CharField(null=True, unique=True)
    email_token = CharField(null=True)
    email_verified = BooleanField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    last_email_token_sent_at = DateTimeField(null=True)
    last_mobile_otp_sent_at = DateTimeField(null=True)
    last_mobile_token_sent_at = DateTimeField(null=True)
    last_whatsapp_otp_sent_at = DateTimeField(null=True)
    lead_user_id = UUIDField(null=True)
    mobile_country_code = CharField(null=True)
    mobile_number = CharField(null=True)
    mobile_number_eformat = CharField(index=True, null=True)
    mobile_otp = CharField(null=True)
    mobile_token = CharField(null=True)
    mobile_token_expiry_at = DateTimeField(null=True)
    mobile_verified = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    name = CharField(null=True)
    password_digest = CharField(null=True)
    picture = CharField(null=True)
    preferred_languages = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    updated_at = DateTimeField()
    used_organization_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    used_partner_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    whatsapp_country_code = CharField(null=True)
    whatsapp_number = CharField(null=True)
    whatsapp_number_eformat = CharField(index=True, null=True)
    whatsapp_otp = CharField(null=True)
    whatsapp_verified = BooleanField(constraints=[SQL("DEFAULT false")], null=True)

    class Meta:
        table_name = 'users'