from datetime import datetime
from database.db_session import db
from peewee import Model
from playhouse.postgres_ext import DateTimeTZField

class BaseModel(Model):
    class Meta:
        database = db
    
class WorkerTimeStamp(BaseModel):
    last_updated_at=datetime.utcnow()

    def save(self,*args, **kwargs):
        self.last_updated_at = datetime.utcnow()
        return super(WorkerTimeStamp, self).save(*args, **kwargs)
    
    class Meta:
        table_name = 'worker_time_stamp'
