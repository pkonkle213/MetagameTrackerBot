from typing import NamedTuple
from models.game import Game
from models.format import Format
from models.store import Store

class Data(NamedTuple):
  Game:Game | None
  Format:Format | None
  Store:Store | None
  UserId:int