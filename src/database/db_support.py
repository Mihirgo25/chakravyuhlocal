from database.db_session import db_state_default, db
from fastapi import Depends
import time
async def reset_db_state():
    db._state._state.set(db_state_default.copy())
    db._state.reset()


def get_db(db_state=Depends(reset_db_state)):
    try:
        s = time.time()
        db.connect()
        print('con: ',time.time() - s)
        yield
    finally:
        if not db.is_closed():
            db.close()
