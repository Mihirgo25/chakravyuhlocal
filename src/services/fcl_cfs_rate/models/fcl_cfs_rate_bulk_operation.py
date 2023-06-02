from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *
import datetime
from fastapi import HTTPException
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rate import list_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate import delete_fcl_cfs_rate
from services.fcl_cfs_rate.models.fcl_cfs_audit import FclCfsRateAudit
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
ACTION_NAMES = ['delete_rate']


class FclCfsRateBulkOperation(Model):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True, index=True)
    service_provider_id = CharField(null = True)
    performed_by_id = CharField(null = True)
    data = BinaryJSONField(null=True)
    progress = IntegerField(null=True)
    action_name = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db
        table_name = 'fcl_cfs_rate_bulk_operations'
        
    def perform_delete_rate_action(self, sourced_by_id, procured_by_id):
        data = self.data
        
        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False})
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
        fcl_cfs_rates = list_fcl_cfs_rate(filters = filters, return_query = True, page_limit = page_limit)['list']
        fcl_cfs_rates = list(fcl_cfs_rates.dicts())

        total_count = len(fcl_cfs_rates)
        count = 0

        for freight in fcl_cfs_rates:
            count += 1

            if FclCfsRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue

            delete_fcl_cfs_rate({
                'id': str(freight.get("id")),
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id,
            })

            self.progress = int((count * 100.0) / total_count)
            self.save()

    def validate_delete_rate_data(self):
        pass