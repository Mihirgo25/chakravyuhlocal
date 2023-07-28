from services.bramhastra.clickhouse.connect import get_clickhouse_client

class StaleS3Dump:
    def __init__(self) -> None:
        self.clickhouse = get_clickhouse_client()
        self.tables = []
    
    def delete_stale_data_from_tables(self):
        for table in self.tables:
            self.clickhouse.execute(f"OPTIMIZE TABLE {table}")
    
    def send_data_to_stale_tables(self):
        for table in self.tables:
            data = self.get_stale_data() 
    
    def send_data_to_s3_and_drop_stale_tables(seld):
        pass 
    
    
    def get_stale_data(self,table):
        return