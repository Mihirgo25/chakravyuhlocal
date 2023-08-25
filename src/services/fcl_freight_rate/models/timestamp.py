from datetime import datetime
from database.db_session import db
from peewee import Model
from playhouse.postgres_ext import DateTimeTZField

class BaseModel(Model):
    class Meta:
        database = db
    
class Timestamp(BaseModel):
    last_updated_at=datetime.utcnow()

    def save(self,*args, **kwargs):
        self.last_updated_at = datetime.utcnow()
        return super(Timestamp, self).save(*args, **kwargs)
    
    class Meta:
        table_name = 'timestamp'
