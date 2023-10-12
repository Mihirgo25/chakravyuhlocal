from enum import Enum


class Chakravyuh(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class ServiceName(Chakravyuh):
    debezium_connect = "debezium_connect"
