from typing import NamedTuple


class Pairing(NamedTuple):
    """Represents a result by pairing"""
    P1Name:str
    P1Wins:int
    P2Name:str
    P2Wins:int
    RoundNumber:int