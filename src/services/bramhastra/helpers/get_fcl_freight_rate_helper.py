from database.rails_db import get_connection
from services.bramhastra.clickhouse.connect import get_clickhouse_client

class FclFreight:
    def __init__(self) -> None:
        self.clickhouse_client = get_clickhouse_client
        self.rails_db = get_connection()
        
        
    def 