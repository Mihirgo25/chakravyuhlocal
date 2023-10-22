from micro_services.discover_client import get_instance_url
from enums.micro_service_enums import ServiceName
from micro_services.global_client import GlobalClient
from enums.global_enums import Host
from configs.env import DEBEZIUM_CONNECT_PORT


class DebeziumConnectApiClient:
    def __init__(self) -> None:
        self.client = GlobalClient(
            url = "http://{}:{}".format(Host.local, DEBEZIUM_CONNECT_PORT),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )

    def create(self, data):
        return self.client.request("POST", "connectors", data)

    def delete(self, name, data={}):
        return self.client.request("DELETE", f"connectors/{name}", data)
        
    def get(self, data={}):
        return self.client.request("GET", f"connectors", data)
