from typing import NamedTuple


class Standing(NamedTuple):
    """Represents a result by standing"""
    PlayerName:str
    Wins:int
    Losses:int
    Draws:int