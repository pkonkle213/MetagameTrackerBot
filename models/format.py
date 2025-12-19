from datetime import date
from typing import NamedTuple

class Format(NamedTuple):
  """Represents a Format"""
  FormatId: int
  Name: str
  LastBanUpdate: date
  IsLimited: bool

class FormatMap(NamedTuple):
  """Represents how a format is mapped"""
  DiscordId:int
  FormatId:int
  ChannelId:int