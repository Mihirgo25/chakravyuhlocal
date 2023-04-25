from database.db_session import db
from peewee_migrate import Router
import time
from pathlib import Path

CURDIR: Path = Path.cwd()
DEFAULT_MIGRATE_DIR: Path = CURDIR / "database" / "migrations"

router = Router(database=db, migrate_dir=DEFAULT_MIGRATE_DIR)
ts = int(time.time())


def create_migration():
    router.create("migration_" + str(ts))


def run_migration():
    router.run()

if __name__ == '__main__':
    create_migration()
