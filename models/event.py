from datetime import date
from typing import NamedTuple


class Event(NamedTuple):
    EventId:int
    StoreDiscordId:int
    EventDate:date
    GameId:int
    FormatId:int
    LastUpdate:date
    EventType:str