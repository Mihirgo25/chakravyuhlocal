from micro_services.discover_client import get_instance_url
from enums.micro_service_enums import ServiceName
from micro_services.global_client import GlobalClient


class DebeziumConnectApiClient:
    def __init__(self) -> None:
        self.client = GlobalClient(
            url = get_instance_url(ServiceName.debezium_connect),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def create(self, data):
        return self.client.request("POST", "connectors", data)

    def delete(self, name, data={}):
        return self.client.request("DELETE", f"connectors/{name}", data)
        
    def get(self, data={}):
        return self.client.request("GET", f"connectors", data)
