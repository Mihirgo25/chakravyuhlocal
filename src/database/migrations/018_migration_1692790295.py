from contextlib import suppress

import peewee as pw
from peewee import *
from peewee_migrate import Migrator
from services.envision.models.air_rate_prediction_feedback import AirFreightRatePredictionFeedback


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your migrations here."""
    migrator.add_fields(AirFreightRatePredictionFeedback, shipment_type = CharField(null=True))
    migrator.add_fields(AirFreightRatePredictionFeedback, stacking_type = CharField(null=True))
    migrator.add_fields(AirFreightRatePredictionFeedback, commodity = CharField(null=True))
    


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    """Write your rollback migrations here."""
    
