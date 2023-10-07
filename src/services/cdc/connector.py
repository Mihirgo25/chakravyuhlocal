from configs.env import (
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_NAME,
    APP_ENV,
)
from micro_services.client import debezium_connect
from enums.global_enums import Platform, Host, AppEnv
import sys

"""
Example:
        # Initialize a Debezium connector with the Brahmastra configuration
        brahmastra_connector = Connector(configs.brahmastra)

        # Create the connector
        brahmastra_connector.create()

        # Delete the connector
        brahmastra_connector.delete()
"""


class Connector:
    def __init__(self, connector: dict) -> None:
        self.connector = connector

    def create(self):
        debezium_connect.create(self.connector)

    def delete(self):
        debezium_connect.delete(self.connector["name"])
        
    def get(self):
        return debezium_connect.get()


class Configs:
    def __init__(self) -> None:
        self.brahmastra = {
            "name": "brahmastra",
            "config": {
                "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
                "tasks.max": "1",
                "plugin.name": "pgoutput",
                "database.hostname": Host.docker_internal
                if sys.platform == Platform.darwin and APP_ENV != AppEnv.production
                else DATABASE_HOST,
                "database.port": DATABASE_PORT,
                "database.user": DATABASE_USER,
                "database.password": DATABASE_PASSWORD,
                "database.dbname": DATABASE_NAME,
                "database.server.name": "ARCTYPE",
                "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                "key.converter.schemas.enable": "false",
                "value.converter.schemas.enable": "false",
                "snapshot.mode": "always",
                "topic.prefix": "arc",
                "table.include.list": "public.fcl_freight_rate_statistics,public.fcl_freight_actions,public.feedback_fcl_freight_rate_statistics,public.fcl_freight_rate_request_statistics"
            },
        }


configs = Configs()
