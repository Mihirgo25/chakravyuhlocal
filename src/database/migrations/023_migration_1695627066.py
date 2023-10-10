"""Peewee migrations -- 023_migration_1695627066.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from services.bramhastra.models.fcl_freight_rate_statistic import FclFreightRateStatistic
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import FeedbackFclFreightRateStatistic
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import CheckoutFclFreightRateStatistic
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import ShipmentFclFreightRateStatistic
from peewee import *
from playhouse.postgres_ext import *
from decimal import ROUND_HALF_EVEN

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL

fields_to_remove = [
    'accuracy',
    'feedback_recieved_count',
    'dislikes_rate_reverted_count',
    'buy_quotations_created',
    'sell_quotations_created',
    'shipment_aborted_count',
    'shipment_cancelled_count',
    'shipment_completed_count',
    'shipment_confirmed_by_importer_exporter_count',
    'shipment_in_progress_count',
    'shipment_received_count',
    'shipment_awaited_service_provider_confirmation_count',
    'shipment_init_count',
    'shipment_containers_gated_in_count',
    'shipment_containers_gated_out_count',
    'shipment_vessel_arrived_count',
    'shipment_is_active_count',
    'shipment_booking_rate_is_too_low_count',
    'version',
    'sign',
    'rate_deviation_from_booking_rate',
    'rate_deviation_from_cluster_base_rate',
    'rate_deviation_from_booking_on_cluster_base_rate',
    'rate_deviation_from_latest_booking',
    'rate_deviation_from_reverted_rate',
    'last_indicative_rate',
    'average_booking_rate',
    'booking_rate_count',
    'total_priority'
 ]

def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    # fcl_freight_rate_statistics
    migrator.add_fields(FclFreightRateStatistic, tag = CharField(max_length=256, null = True))
    migrator.sql(f'Create index fcl_freight_rate_statistic_tag on {FclFreightRateStatistic._meta.table_name} (tag);')
    migrator.add_fields(FclFreightRateStatistic, shipment_completed = IntegerField(default = 0))
    migrator.add_fields(FclFreightRateStatistic, shipment_cancelled = IntegerField(default = 0))
    migrator.add_fields(FclFreightRateStatistic, bas_standard_price_accuracy = FloatField(default = -1))
    migrator.add_fields(FclFreightRateStatistic, bas_standard_price_diff_from_selected_rate = FloatField(default=0))
    migrator.add_fields(FclFreightRateStatistic, parent_rate_mode = CharField(null = True))
    migrator.sql(f'Create index fcl_freight_rate_statistic_parent_rate_mode on {FclFreightRateStatistic._meta.table_name} (parent_rate_mode);')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN accuracy CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN feedback_recieved_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN dislikes_rate_reverted_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN buy_quotations_created CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN sell_quotations_created CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_aborted_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_cancelled_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_completed_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_confirmed_by_importer_exporter_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_in_progress_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_received_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_awaited_service_provider_confirmation_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_init_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_containers_gated_in_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_containers_gated_out_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_vessel_arrived_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_is_active_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_booking_rate_is_too_low_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN version CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN sign CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN rate_deviation_from_booking_rate CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN rate_deviation_from_cluster_base_rate CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN rate_deviation_from_booking_on_cluster_base_rate CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN rate_deviation_from_latest_booking CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN rate_deviation_from_reverted_rate CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN last_indicative_rate CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN average_booking_rate CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN booking_rate_count CASCADE;')
    migrator.sql(f'ALTER TABLE {FclFreightRateStatistic._meta.table_name} DROP COLUMN total_priority CASCADE;')


    # feedback_fcl_freight_rate_statistics
    migrator.add_fields(FeedbackFclFreightRateStatistic, is_rate_reverted = IntegerField(default = 0))

    # checkout_fcl_freight_rate_statistics
    migrator.sql(f'ALTER TABLE {CheckoutFclFreightRateStatistic._meta.table_name} DROP COLUMN sell_quotation_id CASCADE;')
    migrator.sql(f'ALTER TABLE {CheckoutFclFreightRateStatistic._meta.table_name} DROP COLUMN buy_quotation_id CASCADE;')

    # shipment_fcl_freight_rate_statistics
    migrator.sql(f'Create index shipment_fcl_freight_rate_statistics_shipment_id on {ShipmentFclFreightRateStatistic._meta.table_name} (shipment_id);')
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_serial_id = BigIntegerField(null = True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_source = CharField())
    migrator.add_fields(ShipmentFclFreightRateStatistic, containers_count = IntegerField())
    migrator.add_fields(ShipmentFclFreightRateStatistic, cargo_weight_per_container = FloatField())
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_state = TextField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_service_id = UUIDField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_cancelled = IntegerField(default=0))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_cancellation_reason = TextField(default="None"))
    migrator.sql(f'Create index shipment_fcl_freight_rate_statistics_shipment_cancellation_reason on {ShipmentFclFreightRateStatistic._meta.table_name} (shipment_cancellation_reason);')
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_completed = IntegerField(default=0))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_aborted = IntegerField(default=0))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_in_progress = IntegerField(default=0))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_confirmed_by_importer_exporter = IntegerField(default=0))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_recieved = IntegerField(default=0))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_source_id = UUIDField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_created_at = DateTimeTZField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_updated_at = DateTimeTZField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_service_state = CharField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_service_is_active = CharField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_service_created_at = DateTimeTZField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_service_updated_at = DateTimeTZField(null=True))
    migrator.add_fields(ShipmentFclFreightRateStatistic, shipment_service_cancellation_reason = TextField(null=True))
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_fcl_freight_service_id CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN service_state CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN service_is_active CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN service_cancellation_reason CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN service_created_at CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN service_updated_at CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN shipping_line_id CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN service_provider_id CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN serial_id CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN importer_exporter_id CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN shipment_type CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN services CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN source CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN source_id CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN state CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN cancellation_reason CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN buy_quotation_id CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN buy_quotation_created_at CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN buy_quotation_updated_at CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN is_deleted CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN total_price CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN total_price_discounted CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN tax_price CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN tax_price_discounted CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN tax_total_price CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN tax_total_price_discounted CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN currency CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN standard_total_price CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN created_at CASCADE;')
    migrator.sql(f'ALTER TABLE {ShipmentFclFreightRateStatistic._meta.table_name} DROP COLUMN updated_at CASCADE;')






def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

