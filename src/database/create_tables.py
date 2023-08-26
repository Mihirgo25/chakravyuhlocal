from database.db_session import db
from services. bramhastra.models.data_migration import DataMigration
from services.fcl_freight_rate.models.worker_time_stamp import WorkerTimeStamp


class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self,models):
        try:
            db.create_tables(models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = [DataMigration, WorkerTimeStamp]

    Table().create_tables(models)
