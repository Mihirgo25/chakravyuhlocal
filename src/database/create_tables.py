from database.db_session import db


class Table:
    def __init__(self, models) -> None:
        self.models = models

    def create_tables(self):
        try:
            db.create_tables(self.models)
            db.close()
            print("created table")
        except:
            print("Exception while creating table")
            raise


if __name__ == "__main__":
    models = []

    Table(models).create_tables()
