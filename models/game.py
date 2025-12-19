from typing import NamedTuple

class Game(NamedTuple):
  """Represents a game"""
  GameId:int
  Name:str

class GameMap(NamedTuple):
  """Represents how a game is mapped"""
  DiscordId:int
  GameId:int
  CategoryId:int