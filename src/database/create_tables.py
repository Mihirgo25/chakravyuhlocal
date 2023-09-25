from database.db_session import db
from services.bramhastra.models.fcl_freight_action import FclFreightAction

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
    models = [FclFreightAction]

    Table().create_tables(models)
