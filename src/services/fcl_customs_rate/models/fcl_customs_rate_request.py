from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRateRequest(BaseModel):
    id = UUIDField()