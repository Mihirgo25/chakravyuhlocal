from services.bramhastra.clickhouse.connect import get_clickhouse_client

class StaleS3Dump:
    def __init__(self) -> None:
        self.clickhouse = get_clickhouse_client()
        
    
    def send_data_to_stale_tables(self):
        pass 
    
    def send_data_to_s3_and_drop_stale_tables(seld):
        pass 
    
    
    