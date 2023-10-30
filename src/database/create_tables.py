from database.db_session import db
from services.lcl_freight_rate.models.lcl_freight_rate_audit import LclFreightRateAudit

class Table:
    def __init__(self) -> None:
        pass

    def create_tables(self, models):
        try:
            db.create_tables(models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = [
        LclFreightRateAudit
    ]

    Table().create_tables(models)
