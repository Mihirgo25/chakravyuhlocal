from configs.env import (
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_NAME,
)
from micro_services.discover_client import get_instance_url
from micro_services.global_client import GlobalClient

class Connector:
    brahmastra =  {
        "name": "brahmastra",
        "config": {
            "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
            "tasks.max": "1",
            "plugin.name": "pgoutput",
            "database.hostname": DATABASE_HOST,
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
            "topic.prefix": "cdc",
            "table.include.list": "public.fcl_freight_actions,public.fcl_freight_statistics",
        },
    }

    client = GlobalClient(url = get_instance_url('debezium_connect'))

    response = client.request('POST','connectors',data = debezium)

    return response


