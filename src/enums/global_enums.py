from enum import Enum


class Chakravyuh(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class AppEnv(Chakravyuh):
    production = "production"
    development = "development"
    staging = "staging"


class Environment(Chakravyuh):
    cli = "cli"
    app = "app"


class Host(Chakravyuh):
    local = "127.0.0.1"
    docker_internal = "host.docker.internal"


class Context(Chakravyuh):
    common = "common"


class Platform(Chakravyuh):
    darwin = "darwin"


class Action(Chakravyuh):
    create = "create"
    delete = "delete"
    update = "update"
