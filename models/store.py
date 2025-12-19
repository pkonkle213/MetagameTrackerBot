from typing import NamedTuple


class Store(NamedTuple):
    """Represents a store"""
    DiscordId:int
    DiscordName:str
    StoreName:str
    OwnerId:int
    OwnerName:str
    Address:str
    UsedForData:bool
    IsPaid:bool
    State:str
    Region:str
    IsHub:bool