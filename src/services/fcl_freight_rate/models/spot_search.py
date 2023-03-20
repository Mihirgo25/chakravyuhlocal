from peewee import *
from playhouse.postgres_ext import *
from database.db_session import db_rails

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db_rails

class SpotSearch(BaseModel):
    booking_proof = CharField(null=True)
    booking_remark = CharField(null=True)
    can_change_booking_params = BooleanField(null=True)
    consignee_details = BinaryJSONField(null=True)
    created_at = DateTimeField()
    credit_option = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_branch_id = UUIDField(null=True)
    importer_exporter_id = UUIDField(index=True, null=True)
    invoice = BinaryJSONField(null=True)
    is_locked = BooleanField(null=True)
    last_rate_available_date = DateTimeField(null=True)
    margin_approval_manager_assigned_at = DateTimeField(null=True)
    margin_approval_manager_id = UUIDField(null=True)
    margin_approval_managers = UnknownField(constraints=[SQL("DEFAULT '{}'::jsonb[]")], null=True)  # ARRAY
    margin_approval_request_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    margin_approval_requested_by_id = UUIDField(null=True)
    margin_approval_status = CharField(null=True)
    negotiation_response_receiver_id = UUIDField(null=True)
    negotiation_revert_deadline = DateTimeField(null=True)
    negotiation_reverted_services = BinaryJSONField(null=True)
    negotiation_reverts_count = IntegerField(null=True)
    negotiation_services = BinaryJSONField(null=True)
    negotiation_services_deprecated = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    negotiation_status = CharField(null=True)
    notification_sent_at = DateTimeField(null=True)
    notify_me_by = CharField(null=True)
    primary_service_id = UUIDField(null=True)
    quotation_email_sent_at = DateTimeField(null=True)
    quotation_email_sent_by_id = UUIDField(null=True)
    quotation_type = CharField(null=True)
    rates = BinaryJSONField(null=True)
    rates_count = IntegerField(null=True)
    schedules_required = BooleanField(null=True)
    search_type = CharField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('spot_searches_serial_id_seq'::regclass)")], index=True)
    services = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    shipment_id = UUIDField(null=True)
    shipper_details = BinaryJSONField(null=True)
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    terms_and_conditions = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'spot_searches'