from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime


class BaseModel(Model):
    db.execute_sql('CREATE SEQUENCE rate_sheets_serial_id_seq START WITH 1')
    class Meta:
        database = db
class RateSheet(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
    )
    service_provider_id = UUIDField(index=True, null=True)
    service_name = CharField(null=True, index=True)
    file_url = CharField(null=True)
    comment = CharField(null=True)
    status = CharField(null=True, index=True)
    converted_files = JSONField(null=True)
    partner_id = UUIDField(index=True, null=True)
    agent_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    serial_id = BigIntegerField(constraints=[SQL(" DEFAULT nextval('rate_sheets_serial_id_seq')")],)
    cogo_entity_id = UUIDField(index=True, null=True)

    class Meta:
        table_name = 'rate_sheets'

RateSheet.add_index(SQL("CREATE INDEX index_rate_sheets_on_service_provider_id_and_status ON rate_sheets (service_provider_id, status);"))
RateSheet.add_index(SQL("CREATE INDEX index_rate_sheets_on_service_provider_id_and_service_name ON rate_sheets (service_provider_id, service_name);"))
RateSheet.add_index(SQL("CREATE INDEX index_rate_sheets_on_partner_id_and_agent_id_and_status ON rate_sheets (partner_id, agent_id, status);"))
RateSheet.add_index(SQL("CREATE INDEX index_rate_sheets_on_agent_id_and_status ON rate_sheets (agent_id, status);"))
