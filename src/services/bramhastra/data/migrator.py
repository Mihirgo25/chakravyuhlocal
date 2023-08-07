import os
from services.bramhastra.models.data_migration import DataMigration
from peewee import fn
from datetime import datetime
from configs.definitions import ROOT_DIR
import importlib.util


class Migrator:
    def __init__(self):
        self.directory = f"{ROOT_DIR}/services/bramhastra/data/migrations/"
        self.number = self.get_current_number()
        breakpoint()
    def create(self):
        migration_number = self.number + 1
        migration_file = f"migration_{migration_number}.py"
        with open(migration_file, "w") as file:
            file.write(
                f"""def main():
    # Your migration logic goes here
    pass

if __name__ == '__main__':
    main()
"""
            )

    def run(self):
        migrations = (
            DataMigration.select()
            .where(DataMigration.id > self.number)
            .order_by(DataMigration.id.asc())
        )
        executed_migrations = set(migration.id for migration in migrations)

        migration_files = [
            filename
            for filename in os.listdir(self.directory)
            if filename.startswith("migration_") and filename.endswith(".py")
        ]

        migration_files.sort()

        for migration_file in migration_files:
            migration_id = int(migration_file.split("_")[1].split(".")[0])
            if migration_id not in executed_migrations:
                migration_path = os.path.join(self.directory, migration_file)
                spec = importlib.util.spec_from_file_location(
                    f"migration_{migration_id}", migration_path
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"Running migration {migration_id}")
                module.main()
                DataMigration.create(id=migration_id, created_at=datetime.now())

    def get_current_number(self):
        highest_number = -1
        for filename in os.listdir(self.directory):
            try:
                number = int(filename[10:-3])
                if number > highest_number:
                    highest_number = number
            except ValueError:
                pass
        breakpoint()
        return highest_number
        
migrator = Migrator()