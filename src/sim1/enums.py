from enum import StrEnum


class Role(StrEnum):
    WORKER = "worker"
    OWNER = "owner"


class Command(StrEnum):
    HELP = "help"
    H = "h"
    QUIT = "quit"
    Q = "q"
    STOP = "stop"
    START = "start"
    FIRMS = "firms"
    PEOPLE = "people"
    ECONOMY = "economy"
