from models.standing import Standing
from models.pairing import Pairing
from typing import NamedTuple

#TODO: I can probably combined this, standing, and pairing into one file for simplicity
class Result(NamedTuple):
  Data:list[Standing] | list[Pairing] | None
  Errors:list[str]